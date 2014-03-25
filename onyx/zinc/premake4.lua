solution "zinc"
  configurations { "Debug", "Release" }

  project "zinc"
    kind "ConsoleApp"
    language "C++"
    objdir "obj"
    targetname "zinc"
    files { "src/**.h", "src/**.cpp" }

		if os.get() == "macosx" then
      libdirs { "../thirdparty/libs/mac"}
      libdirs { "/opt/local/lib" }
		elseif os.get() == "linux" then
      libdirs { "../thirdparty/libs/linux"}
    end

    includedirs { "src", "protocols" }
    includedirs { "../thirdparty", "../thirdparty/anuvad/src" }
    links { "protobuf" }

    -- Protocol Buffer compile step!
    prebuildcommands { "protoc --cpp_out=protocols -I./protocols protocols/zinc.proto" }
    files { "protocols/zinc.pb.cc" }

    links { "tbb", "tbbmalloc" }

    links { "gdsii", "misc", "z" }
    libdirs { "../thirdparty/anuvad/lib" }

    configuration "Debug"
      defines { "DEBUG" }
      flags { "Symbols" }
      targetdir "debug"

    configuration "Release"
      defines { "NDEBUG" }
      flags { "Optimize", "Symbols" }
      targetdir "release"

