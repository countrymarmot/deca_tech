//
// gds_output_stage.h
// zinc
//
// Created by Craig Bishop on 01 January 2013
// Copyright 2013 All rights reserved
//

#ifndef H_GDS_OUTPUT_STAGE
#define H_GDS_OUTPUT_STAGE

#include "zinc.pb.h"
#include <string>

/*
 * Decompresses GDS data passed in and writes it to a file
 *
 * @param data Raw GDS data bytes
 * @param dataSize Size of raw GDS data buffer
 * @param uncompressed_size Size of GDS file uncompressed
 * @param fp FILE* to write output to
 * @return true on success, false on failure
 */
bool DecompressGDSFromDataToFile(const char* data, const size_t dataSize,
    const size_t uncompressed_size, FILE* fp);

/*
 * Outputs a GDS file for each layer in the design to the
 * zinc::CreateGDSWorkResults message object
 *
 * @param workItem zinc::CreateGDSWorkItem message object
 * @param workResults zinc::CreateGDSWorkResults message object for storing 
 *                    finished results
 * @param verbose Whether to output progress information
 * @return true on success, false on erorr
 */
bool gds_output_stage(const zinc::CreateGDSWorkItem& workItem,
    zinc::CreateGDSWorkResults* workResults, bool verbose);

#endif

