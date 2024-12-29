import re
import json
import os

# ----------------------------------------------------------------------
# Script: vdscript_to_llc_v1.1.0.py
# Description:
# This script converts VirtualDub or VirtualDub2 .vdscript files into 
# LosslessCut .llc files. It is designed to assist users who cut videos 
# using proxy files and want to ensure frame accuracy when applying cuts 
# to the original high-resolution files.
# This script was tested and works with:
# - VirtualDub2 (build 44282) .vdscript files
# - LosslessCut 3.62.0
#
# Features:
# - Convert VirtualDub(.vdscript) cuts into LosslessCut(.llc) format.
# - Option to add extra frames at the beginning and/or end of each cut.
# - Ensures no negative frame values (e.g., if a cut starts at frame 0).
# - User-friendly output with clear error messages.
#
# Note:
#   The "extra_frames_end" feature will not cause any problems if the 
#   frames are added at the very end of your input video (if your last 
#   segment's end point is at the very last frame of the input video). 
#   LosslessCut will display that there are extra frames, but when that 
#   last segment is saved, it's end point will be axactly the same as 
#   if there were no extra frames added to that end point at all! 
#   Likewise, "extra_frames_start" is completely safe also!
#
# Usage:
# 1. Place this script in the same directory as your .vdscript file or specify 
#    the full path to your .vdscript file in the vdscript_filepath variable.
# 2. Edit the script parameters in the "Usage example" section:
#    - `vdscript_filepath`: Path to your .vdscript file.
#    - `llc_filepath`: Desired path for the output .llc file.
#    - `media_filename`: Name of the original video file.
#    - `fps`: Frame rate of your video (e.g., 23.976, 25). 
#       CHECK AND SET THE FRAME RATE TO MATCH THE VIDEO BEING USED!!
#       This is particularly important since the script's accuracy depends on it!
#    - `extra_frames_start`: Frames to add at the beginning of each cut.
#    - `extra_frames_end`: Frames to add at the end of each cut.
# 3. Run the script.
#
# Version History:
# v1.0.0 - Initial script with basic conversion functionality - has 
#          option to include extra frames at the end of each cut.
# v1.1.0 - Added feature to include extra frames at the start of each cut,
#          & added detailed user guide.
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

# Function to parse the .vdscript file and add extra frames to each cut
def parse_vdscript(filepath, fps, extra_frames_start, extra_frames_end):
    """
    Parses the .vdscript file to extract cut ranges and convert them into timecodes.

    Args:
        filepath (str): Path to the .vdscript file.
        fps (float): Frame rate of the video.
        extra_frames_start (int): Number of extra frames to add to the start of each cut.
        extra_frames_end (int): Number of extra frames to add to the end of each cut.

    Returns:
        list: A list of dictionaries representing cut segments with start and end times.
    """
    cut_segments = []

    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    # Regex to match VirtualDub subset lines (e.g., VirtualDub.subset.AddRange(412,208);)
    subset_pattern = re.compile(r'VirtualDub\.subset\.AddRange\((\d+),(\d+)\);')

    for line in lines:
        match = subset_pattern.match(line)
        if match:
            start_frame = int(match.group(1))
            frame_count = int(match.group(2))
            
            # Adjust the start frame, ensuring it doesn't go below 0
            new_start_frame = max(start_frame - extra_frames_start, 0)
            new_end_frame = start_frame + frame_count + extra_frames_end

            # Convert frames to time
            start_time = frames_to_timecode(new_start_frame, fps)
            end_time = frames_to_timecode(new_end_frame, fps)
            
            # Append the segment to the list
            cut_segments.append({
                "start": start_time,
                "end": end_time,
                "name": ""
            })

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
def convert_vdscript_to_llc(vdscript_filepath, llc_filepath, media_filename, fps, extra_frames_start, extra_frames_end):
    """
    Main function to convert a .vdscript file to a .llc file for LosslessCut.

    Args:
        vdscript_filepath (str): Path to the .vdscript file.
        llc_filepath (str): Path to save the .llc file.
        media_filename (str): Name of the original media file.
        fps (float): Frame rate of the video.
        extra_frames_start (int): Number of extra frames to add to the start of each cut.
        extra_frames_end (int): Number of extra frames to add to the end of each cut.
    """
    cut_segments = parse_vdscript(vdscript_filepath, fps, extra_frames_start, extra_frames_end)
    write_llc_file(llc_filepath, media_filename, cut_segments)

# Usage example - EDIT THESE VALUES
if __name__ == "__main__":
    vdscript_filepath = r"C:\New folder\test.vdscript"  # Path to the .vdscript file
    llc_filepath = r"C:\New folder\output.llc"  # Path to save the .llc file
    media_filename = "test.mp4"  # Name of the video file
    fps = ?  # Frame rate of the video - Replace '?' with the correct value (e.g., 23.976, 25)
    extra_frames_start = 0  # Number of frames to add to the start of each cut
    extra_frames_end = 4  # Number of frames to add to the end of each cut
    
    convert_vdscript_to_llc(vdscript_filepath, llc_filepath, media_filename, fps, extra_frames_start, extra_frames_end)
