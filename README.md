# vdscript_to_llc
This script converts VirtualDub or VirtualDub2 .vdscript files into LosslessCut .llc files.
It is designed to assist users who cut videos using proxy files and want to ensure frame accuracy when applying cuts to the original high-resolution files.
This script was tested and works with:
- Python 3.13.2  
- VirtualDub2 (build 44282) .vdscript files
- LosslessCut 3.63.0

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

THIS SECTION ONLY APPLIES IF USING "vdscript_range_adjuster" ADJUSTED VDSCRIPTS
- When processing a "keyframe corrected" vdscript (which was created by "vdscript_range_adjuster"), it is necessary to set "extra_frames_start" to "-4", or possibly more. Otherwise, LosslessCut may go to the previous I frame instead of the current (the wanted) I frame, when exporting the video! - which would not harm the video, but would add lots of unnecessary footage. But before performing that step, it is advisable to run "1stGOP_analyzer" (which comes with "vdscript_range_adjuster") on the "keyframe corrected" vdscript, to make sure that there are no ultra short GOPs at the start of any of the ranges. As long as the shortest GOP is longer than your "extra_frames_start" negative value, you will not lose any frames. "extra_frames_end" (in the case of "keyframe corrected" vdscripts) is fine set at "0", & needs no adjusting :)

- If not working with a "keyframe corrected" vdscript, it is up to you to decide what the values are for "extra_frames_start" & "extra_frames_end". If e.g., you used a proxy video for your editing in VirtualDub, & that proxy wasn't frame-accurate, then it would probably be best to give both options a value of "50" or more, just to be on the safe side :)
- It's important to know - positive values always ADD frames, & negative values always REMOVE frames from your segments!

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

Version History:
v1.0.0 - Initial script with basic conversion functionality - has option to include extra frames at the end of each cut.
v1.1.0 - Added feature to include extra frames at the start of each cut.
v1.2.0 - Added segment numbering functionality for each cut.
v1.3.0 - Allowed negative values for extra_frames_start and extra_frames_end, handling edge cases to prevent invalid segments.