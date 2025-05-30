# vdscript_to_llc
This script converts VirtualDub or VirtualDub2 .vdscript files into LosslessCut .llc files.
WARNING: NOT FRAME ACCURATE! (Hence the "extra_frames_x" parameters).
This script was tested and works with:
- Python 3.13.2  
- VirtualDub2 (build 44282) .vdscript files
- LosslessCut 3.65.0

Features:
- Convert VirtualDub(.vdscript) cuts into LosslessCut(.llc) format.
- Option to add or remove frames at the beginning and/or end of each cut.
- Option to automatically add segment numbers to the "name" field of each cut (e.g., "segment 1", "segment 2", etc.).

Note:
- The `extra_frames_start` and `extra_frames_end` parameters can now accept negative values to remove frames from the start or end of each segment.
- If a negative value for `extra_frames_start` causes the start frame to go below 0, the script will adjust the start frame to 0.
- If the adjusted end frame becomes less than or equal to the adjusted start frame (resulting in a non-positive duration), the script will skip that segment and issue a warning.
- When using negative values, care must be taken to ensure that segments remain valid.
- ABOUT THE "extra_frames_end" FEATURE:
  The "extra_frames_end" feature will not cause any problems if the frames are added at the very end of your input video (if your last segment's end point is at the very last frame of the input video). LosslessCut will display that there are extra frames, but when that last segment is saved, its end point will be exactly the same as if there were no extra frames added to that end point at all!
- It's important to know that for both "extra_frames_start" & 
  "extra_frames_end", positive values always ADD frames, & negative 
  values always REMOVE frames from your segments!

Usage:
1. Place this script in the same directory as your .vdscript file or specify the full path to your .vdscript file in the `vdscript_filepath` variable.
2. Edit the script parameters in the "Usage example" section:
- `vdscript_filepath`: Path to your .vdscript file.
- `llc_filepath`: Desired path for the output .llc file.
- `media_filename`: Name of the original video file.
- `fps`: Frame rate of your video (e.g., 23.976, 25). CHECK AND SET THE FRAME RATE TO MATCH THE VIDEO BEING USED!! This is particularly important since the script's accuracy depends on it!
- `extra_frames_start`: Frames to add/remove at the beginning of each cut (can be negative).
- `extra_frames_end`: Frames to add/remove at the end of each cut (can be negative).
- `add_segment_number`: Set this to True to add numbering (e.g., "segment 1").
3. Run the script.
