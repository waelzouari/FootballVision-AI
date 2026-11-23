# FootballVision collaborator handoff

This repository contains the reproducible P0 source, configuration, tests and
text reports.  It deliberately does **not** contain model weights, videos or
generated outputs.

1. Clone the repository.
2. Follow the operating-system guide: [macOS](SETUP_MAC.md) or
   [Windows](SETUP_WINDOWS.md).
3. Obtain the model using [MODEL_SOURCES.md].
4. Provide a video you are entitled to use, then run the command in
   [VERIFY_INSTALLATION.md].

The automated test suite does not need a model or video.  The P0 end-to-end
demo needs both a local YOLO weights file and a readable MP4.  Paths are CLI
arguments, so no machine-specific path is stored in the code.

See [FILES_TO_TRANSFER.md](FILES_TO_TRANSFER.md) for the local inventory and
transfer restrictions.
