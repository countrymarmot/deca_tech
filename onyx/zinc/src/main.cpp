//
// main.cpp
// zinc
//
// Created by Craig Bishop on 29 November 2012
// Copyright 2012 All rights reserved
//

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string>
#include "optionparser-1.3/optionparser.h"
#include <google/protobuf/text_format.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>
#include "zinc.pb.h"
#include "o4engine/cpu_route_stage.h"
#include "gdsout/gds_output_stage.h"
#include "smoother/smooth_stage.h"

// Command-line option definition
enum optionIndex
{
  UNKNOWN,
  OUTPUT_FILE,
  INPUT_FILE,
  DEBUG_MODE,
  MANUAL_MODE,
  ONYX_FILE,
  SHIFTS_FILE,
  WAIT_START,
  DEBUG_LAYER
};

// Helper for checking a CLI argument exists
struct Arg : public option::Arg
{
  static option::ArgStatus Required(const option::Option& option, bool msg)
  {
    if (option.arg != 0)
      return option::ARG_OK;
    if (msg)
      printf("ERROR: Option '%s' requires an argument\n\n", option.name);
    return option::ARG_ILLEGAL;
  }
};

// Command-line option details
const option::Descriptor usage[] =
{
  {UNKNOWN,     0, "",  "",       Arg::None,
      "USAGE: zinc [options]\n\nOptions:" },
  {OUTPUT_FILE, 0, "o", "output", Arg::Required,
      "  --output, -o <file>  \tDirect output to file"},
  {INPUT_FILE,  0, "i", "input", Arg::Required,
      "  --input, -i <file>  \tLoad input from file"},
  {DEBUG_MODE,  0, "d", "debug", Arg::None,
      "  --debug, -d \tOutput additional debug information"},
  {MANUAL_MODE, 0, "m", "manual", Arg::None,
      "  --manual, -m \tRun Onyx in traditional manual mode"},
  {ONYX_FILE,   0, "f", "onyxfile", Arg::Required,
      "  --onyxfile, -f \tInput Onyx file for manual mode"},
  {SHIFTS_FILE, 0, "s", "shifts", Arg::Required,
      "  --shifts, -s \tInput shifts file for manual mode"},
  {WAIT_START, 0, "p", "pause", Arg::None,
      "  --pause, -p \tWaits for a key-press before running"},
  {DEBUG_LAYER, 0, "l", "pause", Arg::Required,
      "  --debuglayer, -l \tWrites additional debug info to a GDS layer"},
  {0, 0, 0, 0, 0, 0}
};


/// Parsed options for running Onyx
struct RunOptions
{
  bool parseError;
  bool manualMode;
  bool hasOutputFile;
  bool hasInputFile;
  bool debug;
  bool waitStart;
  std::string outputFile;
  std::string inputFile;
  std::string onyxFile;
  std::string shiftsFile;
  bool outputDebugLayer;
  int debugLayer;

  RunOptions()
  {
    parseError = false;
    manualMode = false;
    hasOutputFile = false;
    hasInputFile = false;
    debug = false;
    waitStart = false;
    outputDebugLayer = false;
  }
};

/*
 * Parses command line arguments into a RunOptions structure
 *
 * @param argc argc passed to int main(..)
 * @param argv argv passed to int main(..)
 * @return Filled RunOptions structure
 */
RunOptions parseOptions(int argc, char* argv[])
{
  RunOptions runOptions;
  option::Stats stats(usage, argc, argv);
  option::Option* options = new option::Option[stats.options_max];
  option::Option* buffer  = new option::Option[stats.buffer_max];
  option::Parser parse(usage, argc, argv, options, buffer);

  // if not enough args or parse error, print usage and fail out
  if (parse.error() || argc == 0)
  {
    option::printUsage(std::cout, usage);
    runOptions.parseError = true;
    delete[] options;
    delete[] buffer;
    return runOptions;
  }

  // check for debug
  if (options[DEBUG_MODE])
    runOptions.debug = true;

  // check for waiting start
  if (options[WAIT_START])
    runOptions.waitStart = true;

  // if in manual mode, expect onyx file and shifts file
  if (options[MANUAL_MODE])
  {
    if (!(options[ONYX_FILE] && options[SHIFTS_FILE]))
    {
      printf("Manual mode requires a .onyx file and a shifts file\n\n");
      runOptions.parseError = true;
      delete[] options;
      delete[] buffer;
      return runOptions;
    }
    runOptions.manualMode = true;
    runOptions.onyxFile = std::string(options[ONYX_FILE].arg);
    runOptions.shiftsFile = std::string(options[SHIFTS_FILE].arg);

    if (options[DEBUG_LAYER])
    {
      runOptions.outputDebugLayer = true;
      runOptions.debugLayer = atoi(options[DEBUG_LAYER].arg);
    }
  }

  // not in manual mode, so only input/output options
  if (options[OUTPUT_FILE])
  {
    runOptions.hasOutputFile = true;
    runOptions.outputFile = std::string(options[OUTPUT_FILE].arg);
  }
  if (options[INPUT_FILE])
  {
    runOptions.hasInputFile = true;
    runOptions.inputFile = std::string(options[INPUT_FILE].arg);
  }

  delete[] options;
  delete[] buffer;
  return runOptions;
}

/*
 * Returns an istream for the input message based on
 * options; could be stdin or a file
 *
 * @param options RunOptions parsed from CLI
 * @return istream* for the input message; caller owns pointer
 */
std::istream* selectInputStream(const RunOptions& options)
{
  if (options.hasInputFile)
    return new std::ifstream(options.inputFile.c_str(), std::ios::binary);
  return &std::cin;
}

/*
 * Returns an ostream for the output message based on
 * options; could be stdout or a file
 *
 * @param options RunOptions parsed from CLI
 * @return ostream* for the output message; caller owns pointer
 */
std::ostream* selectOutputStream(const RunOptions& options)
{
  if (options.hasOutputFile)
    return new std::ofstream(options.outputFile.c_str(), std::ios::binary);
  return &std::cout;
}

/*
 * Sends a WorkResult message indicating an error has occurred
 *
 * @param workResult Outgoing WorkResult message
 * @param errorMessage Error message text
 */
void createErrorWorkResult(zinc::WorkResult& workResult, std::string errorMessage)
{
  workResult.set_success(false);
  workResult.set_errormessage(errorMessage);
}

/*
 * Dispatches an incoming WorkItem depending on
 * what kind it is
 *
 * @param workItem Incoming WorkItem message
 * @param workResult Outgoing WorkResult message; process fills this
 * @param verbose Whether to output progess information
 */
void processWorkItem(const zinc::WorkItem& workItem, zinc::WorkResult& workResult,
    bool verbose = false)
{
  zinc::WorkType worktype = workItem.worktype();
  workResult.set_worktype(worktype);
  bool success = false;
  switch (worktype)
  {
    case zinc::ROUTING:
      success = o4::cpu_route_stage(workItem.routingworkitem(),
          workResult.mutable_routingworkresults(), verbose);
      // two smoothing stages
      success |= smoother::smooth_stage(workItem.routingworkitem(),
          workResult.mutable_routingworkresults(), verbose);
      success |= smoother::smooth_stage(workItem.routingworkitem(),
          workResult.mutable_routingworkresults(), verbose);
      break;
    case zinc::CREATE_GDS:
      success = gds_output_stage(workItem.creategdsworkitem(),
          workResult.mutable_creategdsworkresults(), verbose);
      break;
    default:
      createErrorWorkResult(workResult, "Unknown WorkItem type");
      break;
  }
  workResult.set_success(success);
}

/*
 * Loads a .onyx file for manual mode
 *
 * @param fileName Path to .onyx file
 * @param designMessage zinc::Design message object to fill
 * @return true on success, false on error
 */
bool loadOnyxFile(std::string fileName, zinc::Design& design)
{
  std::ifstream* designInput = new std::ifstream(fileName.c_str(),
      std::ios::binary);
  if (!*designInput)
  {
    printf("ERROR: Could not open Onyx file %s\n", fileName.c_str());
    return false;
  }
  if (!design.ParseFromIstream(designInput))
  {
    printf("ERROR: Could not parse Onyx file %s\n", fileName.c_str());
    return false;
  }
  delete designInput;
  return true;
}

/*
 * Loads a shift file for manual mode
 *
 * @param fileName Path to shifts file
 * @param shiftsMessage zinc::Shifts message object to fill
 * @return true on success, false on error
 */
bool loadShiftsFile(std::string fileName, zinc::Shifts& shifts)
{
  // load the shifts using protobuf TextFormat
  std::ifstream* shiftsInput = new std::ifstream(fileName.c_str(),
      std::ios::binary);
  if (!*shiftsInput)
  {
    printf("ERROR: Could not open shifts file %s\n", fileName.c_str());
    return false;
  }
  google::protobuf::io::IstreamInputStream shiftsStream(shiftsInput);
  if (!google::protobuf::TextFormat::Parse(&shiftsStream, &shifts))
  {
    printf("ERROR: Could not parse shifts file %s\n", fileName.c_str());
    return false;
  }
  delete shiftsInput;
  return true;
}

/*
 * Verifies that the manually inputed files match
 *
 * @param design Loaded zinc::Design message object
 * @param shifts Loaded zinc::Shifts message object
 * @return true if successfuly verified, false on error
 */
bool verifyManualInputs(const zinc::Design& design, const zinc::Shifts& shifts)
{
  if ((shifts.designnumber().compare(design.designnumber()) != 0) ||
      shifts.designrevision().compare(design.designrevision()) != 0)
  {
    std::string shiftsVersion = shifts.designnumber() + "_" + shifts.designrevision();
    std::string designVersion = design.designnumber() + "_" + design.designrevision();
    printf("ERROR: Shifts are not for this design\n");
    printf("\tOnyx file version: %s\n", designVersion.c_str());
    printf("\tShifts file version: %s\n", shiftsVersion.c_str());
    return false;
  }
  return true;
}

/*
 * Creates a WorkItem and runs the routing process on it
 *
 * @param design Loaded zinc::Design message object
 * @param shifts Loaded zinc::Shifts message object
 * @param workResult zinc::WorkResult to fill with results
 * @return true on success, false on error
 */
bool runManualRouting(const zinc::Design& design, const zinc::Shifts& shifts,
    zinc::WorkResult& workResult)
{
  // create a WorkItem to run processWorkItem with
  zinc::WorkItem workItem;
  workItem.set_worktype(zinc::ROUTING);
  zinc::RoutingWorkItem* routingWorkItem = workItem.mutable_routingworkitem();
  routingWorkItem->set_panelid(shifts.panelid());
  routingWorkItem->mutable_design()->CopyFrom(design);
  routingWorkItem->mutable_shifts()->CopyFrom(shifts);
  routingWorkItem->mutable_workrange()->set_start(0);
  routingWorkItem->mutable_workrange()->set_end(shifts.units_size() - 1);
  // run routing step
  processWorkItem(workItem, workResult, true);
  if (!workResult.success())
  {
    printf("ERROR: %s\n", workResult.errormessage().c_str());
    return false;
  }
  return true;
}

/*
 * Creates a WorkItem and runs the CreateGDS process on it
 *
 * @param design Loaded zinc::Design message object
 * @param shifts Loaded zinc::Shifts message object
 * @param routingResult zinc::WorkResult objects from runManualRouting
 * @param workResult zinc::WorkResult to fill with results
 * @return true on success, false on error
 */
bool runManualCreateGDS(const zinc::Design& design, const zinc::Shifts& shifts,
    const zinc::WorkResult& routingResult, zinc::WorkResult& workResult,
    bool outputDebugLayer, int debugLayer=0)
{
  // create a WorkItem to run processWorkItem with
  zinc::WorkItem workItem;
  workItem.set_worktype(zinc::CREATE_GDS);
  zinc::CreateGDSWorkItem* createGDSWorkItem = workItem.mutable_creategdsworkitem();
  createGDSWorkItem->mutable_design()->CopyFrom(design);
  createGDSWorkItem->mutable_shifts()->CopyFrom(shifts);
  // copy over the RoutedUnits
  const zinc::RoutingWorkResults* routing = &routingResult.routingworkresults();
  for (int i = 0; i < routing->routedunits_size(); i++)
  {
    zinc::RoutedUnit* unit = createGDSWorkItem->add_routedunits();
    unit->CopyFrom(routing->routedunits(i));
  }
  if (outputDebugLayer)
    createGDSWorkItem->set_debuglayer(debugLayer);

  // run CreateGDS step
  processWorkItem(workItem, workResult, true);
  if (!workResult.success())
  {
    printf("ERROR: %s\n", workResult.errormessage().c_str());
    return false;
  }
  return true;
}

/*
 * Writes GDS files to disk from results
 *
 * @param gdsWorkResult zinc::CreateGDSWorkResults message object
 * @return true on success, false on error
 */
bool writeGDSFiles(const zinc::Design& design,
    const zinc::CreateGDSWorkResults& gdsWorkResult)
{
  std::string prefix = design.designnumber() + "_" +
      design.designrevision() + "_";
  for (int i = 0; i < gdsWorkResult.files_size(); i++)
  {
    const zinc::File& file = gdsWorkResult.files(i);
    std::string filename = prefix + file.filename();
    FILE* fp = fopen(filename.c_str(), "wb");
    if (!fp)
      return false;
    DecompressGDSFromDataToFile(file.data().c_str(), file.data().size(),
        file.uncompressedsize(), fp);
    fclose(fp);
  }
  return true;
}

/*
 * Runs the manual (legacy) process for a single panel
 * based on the inputs supplied to the zinc executable itself
 *
 * @return true on success, false on error
 */
bool runManualMode(const RunOptions& options)
{
  // first try to grab the Onyx file and shifts
  zinc::Design design;
  if (options.debug)
    printf("DEBUG: Loading .onyx file\n");
  if (!loadOnyxFile(options.onyxFile, design))
    return false;
  if (options.debug)
  {
    printf("DEBUG: Loaded .onyx file\n");
    printf("DEBUG: Loading shifts file\n");
  }
  zinc::Shifts shifts;
  if (!loadShiftsFile(options.shiftsFile, shifts))
    return false;
  if (options.debug)
  {
    printf("DEBUG: Loaded shifts file\n");
    printf("DEBUG: This is panel: %s\n", shifts.panelid().c_str());
  }
  if (!verifyManualInputs(design, shifts))
    return false;
  if (options.debug)
  {
    printf("DEBUG: Files verified\n");
    printf("DEBUG: Starting routing\n");
  }
  zinc::WorkResult routingResult;
  if (!runManualRouting(design, shifts, routingResult))
    return false;
  if (options.debug)
  {
    printf("DEBUG: Routing complete\n");
    printf("DEBUG: Creating GDS\n");
  }
  zinc::WorkResult createGDSResult;
  if (!runManualCreateGDS(design, shifts, routingResult, createGDSResult,
        options.outputDebugLayer, options.debugLayer))
    return false;
  if (!writeGDSFiles(design, createGDSResult.creategdsworkresults()))
    return false;
  if (options.debug)
    printf("DEBUG: GDS files complete\n");
  
  return true;
}

int main(int argc, char* argv[])
{
  // verify that the version of Google protobuf in the zinc.pb.h header
  // is compatible with the version zinc is linked against
  GOOGLE_PROTOBUF_VERIFY_VERSION;

  // skip program name argv[0] if present
  argc -= (argc > 0);
  argv += (argc > 0);
  RunOptions options = parseOptions(argc, argv);
  if (options.parseError)
    return 1;

  if (options.waitStart)
    getchar();

  if (options.manualMode)
  {
    // if we're in manual mode, let the manual mode module take
    // care of running the correct work
    if (!runManualMode(options))
      return 1;
  }
  else
  {
    // create WorkResult first so we can send errors if necessary
    zinc::WorkResult workResult;

    // for production mode, first see where the input message
    // comes from
    std::istream* messageInput = selectInputStream(options);
    if (!*messageInput)
    {
      createErrorWorkResult(workResult, "Could not open input stream");
      return 0;
    }

    zinc::WorkItem workItem;
    bool success = workItem.ParseFromIstream(messageInput);
    delete messageInput;
    if (!success)
    {
      createErrorWorkResult(workResult, "Could not parse WorkItem");
      return 0;
    }

    // process the item
    processWorkItem(workItem, workResult, options.debug);

    // find output stream
    std::ostream* messageOutput = selectOutputStream(options);
    if (!messageOutput)
      return 1;

    // output WorkResult
    if (!workResult.SerializeToOstream(messageOutput))
    {
      return 1;
    }
    messageOutput->flush();
    delete(messageOutput);
  }

  return 0;
}

