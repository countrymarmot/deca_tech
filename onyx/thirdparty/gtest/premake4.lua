solution "gtest"
  configurations { "Debug", "Release" }

  project "gtest"
    kind "StaticLib"
    language "C++"
    files { "src/gtest-all.cc" }
    includedirs { ".", "include" }
    objdir "obj"

    configuration "Debug"
      defines { "DEBUG" }
      flags { "Symbols" }
      targetdir "debug"

    configuration "Release"
      defines { "NDEBUG" }
      flags { "Optimize" }
      targetdir "bin"
    
