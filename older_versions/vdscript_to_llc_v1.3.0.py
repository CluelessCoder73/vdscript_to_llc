import re
import json
import os

# ----------------------------------------------------------------------
# Script: vdscript_to_llc_v1.3.0.py
# Description:
# This script converts VirtualDub or VirtualDub2 .vdscript files into 
# LosslessCut .llc files. It is designed to assist users who cut videos 
# using proxy files and want to ensure frame accuracy when applying cuts 
# to the original high-resolution files.
# This script was tested and works with:
# - Python 3.13.2   
# - VirtualDub2 (build 44282) .vdscript files
# - LosslessCut 3.64.0
# 
# Features:
# - Convert VirtualDub(.vdscript) cuts into LosslessCut(.llc) format.
# - Option to add or remove frames at the beginning and/or end of each cut.
# - Ensures no negative frame values (e.g., if a cut starts at frame 0).
# - Prevents segments from having a non-positive duration after adjustments.
# - Option to automatically add segment numbers to the "name" field of 
#   each cut (e.g., "segment 1", "segment 2", etc.).
#
# Note:
#   - The `extra_frames_start` and `extra_frames_end` parameters can now accept 
#     negative values to remove frames from the start or end of each segment.
#   - If a negative value for `extra_frames_start` causes the start frame to go 
#     below 0, the script will adjust the start frame to 0.
#   - If the adjusted end frame becomes less than or equal to the adjusted start 
#     frame (resulting in a non-positive duration), the script will skip that segment 
#     and issue a warning.
#   - When using negative values, care must be taken to ensure that segments remain valid.
#   - ABOUT THE "extra_frames_end" FEATURE:
#     The "extra_frames_end" feature will not cause any problems if the 
#     frames are added at the very end of your input video (if your last 
#     segment's end point is at the very last frame of the input video). 
#     LosslessCut will display that there are extra frames, but when that 
#     last segment is saved, its end point will be exactly the same as 
#     if there were no extra frames added to that end point at all!

###THIS SECTION ONLY APPLIES IF USING "vdscript_range_adjuster" ADJUSTED VDSCRIPTS###
#   - When processing a "keyframe corrected" vdscript (which was created 
#     by "vdscript_range_adjuster"), it is necessary to set 
#     "extra_frames_start" to "-4", or possibly more. Otherwise, 
#     LosslessCut may go to the previous I frame instead of the current 
#     (the wanted) I frame, when exporting the video! - which would not 
#     harm the video, but would add lots of unnecessary footage. 
#     But before performing that step, it is advisable to run 
#     "1stGOP_analyzer" (which comes with "vdscript_range_adjuster") on 
#     the "keyframe corrected" vdscript, to make sure that there are no 
#     ultra short GOPs at the start of any of the ranges. As long as the 
#     shortest GOP is longer than your "extra_frames_start" negative 
#     value, you will not lose any frames.
#     "extra_frames_end" (in the case of "keyframe corrected" vdscripts) 
#     is fine set at "0", & needs no adjusting :)

#   - If not working with a "keyframe corrected" vdscript, it is up to 
#     you to decide what the values are for "extra_frames_start" & 
#     "extra_frames_end". If e.g., you used a proxy video for your 
#     editing in VirtualDub, & that proxy wasn't frame-accurate, then it 
#     would probably be best to give both options a value of "50" or 
#     more, just to be on the safe side :)
#   - It's important to know - positive values always ADD frames, & negative 
#     values always REMOVE frames from your segments!
#
# Usage:
# 1. Place this script in the same directory as your .vdscript file or specify 
#    the full path to your .vdscript file in the `vdscript_filepath` variable.
# 2. Edit the script parameters in the "Usage example" section:
#    - `vdscript_filepath`: Path to your .vdscript file.
#    - `llc_filepath`: Desired path for the output .llc file.
#    - `media_filename`: Name of the original video file.
#    - `fps`: Frame rate of your video (e.g., 23.976, 25). 
#       CHECK AND SET THE FRAME RATE TO MATCH THE VIDEO BEING USED!!
#       This is particularly important since the script's accuracy depends on it!
#    - `extra_frames_start`: Frames to add/remove at the beginning of each cut (can be negative).
#    - `extra_frames_end`: Frames to add/remove at the end of each cut (can be negative).
#    - `add_segment_number`: Set this to True to add numbering (e.g., "segment 1").
# 3. Run the script.
#
# Version History:
# v1.0.0 - Initial script with basic conversion functionality - has 
#          option to include extra frames at the end of each cut.
# v1.1.0 - Added feature to include extra frames at the start of each cut.
# v1.2.0 - Added segment numbering functionality for each cut.
# v1.3.0 - Allowed negative values for extra_frames_start and extra_frames_end, 
#          handling edge cases to prevent invalid segments.
# ----------------------------------------------------------------------

# Function to convert frame number to time in seconds
def frames_to_timecode(frames, fps):
    """
    Converts a frame number to a timecode in seconds.

    Args:
        frames (int): The frame number.
        fps (float): The frame rate of the video.

    Returns:
        float: The timecode in seconds, rounded to 3 decimal places.
    """
    return round(frames / fps, 3)

# Function to parse the .vdscript file and adjust frames for each cut
def parse_vdscript(filepath, fps, extra_frames_start, extra_frames_end, add_segment_number=False):
    """
    Parses the .vdscript file to extract cut ranges and convert them into timecodes.

    Args:
        filepath (str): Path to the .vdscript file.
        fps (float): Frame rate of the video.
        extra_frames_start (int): Number of frames to add/remove at the start of each cut (can be negative).
        extra_frames_end (int): Number of frames to add/remove at the end of each cut (can be negative).
        add_segment_number (bool): Whether to add segment numbers in the "name" field.

    Returns:
        list: A list of dictionaries representing cut segments with start and end times.
    """
    cut_segments = []

    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    # Regex to match VirtualDub subset lines (e.g., VirtualDub.subset.AddRange(412,208);)
    subset_pattern = re.compile(r'VirtualDub\.subset\.AddRange\((\d+),(\d+)\);')

    segment_number = 1  # Initialize the segment counter

    for line in lines:
        match = subset_pattern.match(line)
        if match:
            start_frame = int(match.group(1))
            frame_count = int(match.group(2))
            
            # Adjust the start frame
            new_start_frame = start_frame - extra_frames_start
            # Ensure start frame is not negative
            new_start_frame = max(new_start_frame, 0)
            
            # Adjust the end frame
            new_end_frame = start_frame + frame_count + extra_frames_end

            # Ensure end frame is greater than start frame
            if new_end_frame <= new_start_frame:
                print(f"Warning: Segment {segment_number} has non-positive duration after adjusting frames. Skipping this segment.")
                segment_number += 1
                continue

            # Convert frames to time
            start_time = frames_to_timecode(new_start_frame, fps)
            end_time = frames_to_timecode(new_end_frame, fps)

            # Name the segment with the segment number if requested
            segment_name = f"segment {segment_number}" if add_segment_number else ""

            # Append the segment to the list
            cut_segments.append({
                "start": start_time,
                "end": end_time,
                "name": segment_name
            })

            segment_number += 1  # Increment the segment number

    return cut_segments

# Function to write the LosslessCut .llc file
def write_llc_file(output_filepath, media_filename, cut_segments):
    """
    Writes the cut segments to a LosslessCut .llc file in JSON format.

    Args:
        output_filepath (str): Path to save the .llc file.
        media_filename (str): Name of the original media file.
        cut_segments (list): List of dictionaries representing cut segments.
    """
    if os.path.exists(output_filepath):
        print(f"Error: The file {output_filepath} already exists. Please choose a different filename or remove the existing file.")
        return
    
    llc_data = {
        "version": 1,
        "mediaFileName": media_filename,
        "cutSegments": cut_segments
    }

    with open(output_filepath, 'w') as file:
        json.dump(llc_data, file, indent=2)
    
    print(f"LosslessCut file saved as {output_filepath}")

# Main function to perform the conversion
def convert_vdscript_to_llc(vdscript_filepath, llc_filepath, media_filename, fps, extra_frames_start, extra_frames_end, add_segment_number=False):
    """
    Main function to convert a .vdscript file to a .llc file for LosslessCut.

    Args:
        vdscript_filepath (str): Path to the .vdscript file.
        llc_filepath (str): Path to save the .llc file.
        media_filename (str): Name of the original media file.
        fps (float): Frame rate of the video.
        extra_frames_start (int): Number of frames to add/remove at the start of each cut (can be negative).
        extra_frames_end (int): Number of frames to add/remove at the end of each cut (can be negative).
        add_segment_number (bool): Whether to add segment numbers in the "name" field.
    """
    cut_segments = parse_vdscript(vdscript_filepath, fps, extra_frames_start, extra_frames_end, add_segment_number)
    if cut_segments:
        write_llc_file(llc_filepath, media_filename, cut_segments)
    else:
        print("No valid segments to write to the LosslessCut file.")

# Usage example - EDIT THESE VALUES
if __name__ == "__main__":
    vdscript_filepath = r"C:\New folder\test.vdscript"  # Path to the .vdscript file
    llc_filepath = r"C:\New folder\output.llc"  # Path to save the .llc file
    media_filename = "test.mp4"  # Name of the video file
    fps = ?  # Frame rate of the video - Replace '?' with the correct value (e.g., 23.976, 25)
    extra_frames_start = -4  # Number of frames to add/remove at the start of each cut (can be negative)
    extra_frames_end = 0  # Number of frames to add/remove at the end of each cut (can be negative)
    add_segment_number = False  # Set to True to add segment numbers in the "name" field

    convert_vdscript_to_llc(vdscript_filepath, llc_filepath, media_filename, fps, extra_frames_start, extra_frames_end, add_segment_number)
