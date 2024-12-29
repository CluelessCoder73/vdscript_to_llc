import re
import json
import os

# ----------------------------------------------------------------------
# Script: vdscript_to_llc_v1.0.0.py
# Description: Converts VirtualDub or VirtualDub2 .vdscript files into 
#              LosslessCut .llc files, allowing for frame-accurate cuts
#              with added flexibility for proxy workflows.
# This script was tested and works with:
# - VirtualDub2 (build 44282) .vdscript files
# - LosslessCut 3.62.0
#
# Usage:
# - Set the `vdscript_filepath` to the path of your .vdscript file.
# - Set the `llc_filepath` to where you want to save the output .llc file.
# - Set the `media_filename` to the name of the original video file.
# - Set the `fps` to the frame rate of your video (e.g., 23.976, 25).
# - Optionally set `extra_frames` to add a buffer at the end of each cut.
#
# Example:
#     vdscript_filepath = r"C:\path\to\input.vdscript"
#     llc_filepath = r"C:\path\to\output.llc"
#     media_filename = "video.mp4"
#     fps = 23.976
#     extra_frames = 16  # Set to 0 if no extra frames are needed.
#
# Notes:
# - This script is designed to work with both VirtualDub and VirtualDub2
#   .vdscript files, as long as they use the same `subset.AddRange` syntax.
# - The `extra_frames` parameter helps avoid issues with B-frames when 
#   working with proxy files, by adding a buffer at the end of each cut.
#   Note that these extra frames will not cause any problems if they are
#   added at the very end of your input video (if your last segment's 
#   end point is at the very last frame of the input video). LosslessCut
#   will display that there are extra frames, but when that last segment
#   is saved, it will be identical to if there were no extra frames added!
# ----------------------------------------------------------------------

# Function to convert frame number to time in seconds
def frames_to_timecode(frames, fps):
    """
    Converts a frame number to a timecode in seconds.
    
    Args:
        frames (int): The frame number.
        fps (float): The frame rate of the video.
    
    Returns:
        float: The timecode in seconds.
    """
    return round(frames / fps, 3)

# Function to parse the .vdscript file and add extra frames to the end of each cut
def parse_vdscript(filepath, fps, extra_frames):
    """
    Parses the .vdscript file to extract cut ranges and convert them into timecodes.

    Args:
        filepath (str): Path to the .vdscript file.
        fps (float): Frame rate of the video.
        extra_frames (int): Number of extra frames to add to the end of each cut.

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
            end_frame = start_frame + frame_count + extra_frames  # Add extra frames to the end
            
            # Convert frames to time
            start_time = frames_to_timecode(start_frame, fps)
            end_time = frames_to_timecode(end_frame, fps)
            
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
def convert_vdscript_to_llc(vdscript_filepath, llc_filepath, media_filename, fps, extra_frames):
    """
    Main function to convert a .vdscript file to a .llc file for LosslessCut.

    Args:
        vdscript_filepath (str): Path to the .vdscript file.
        llc_filepath (str): Path to save the .llc file.
        media_filename (str): Name of the original media file.
        fps (float): Frame rate of the video.
        extra_frames (int): Number of extra frames to add to the end of each cut.
    """
    cut_segments = parse_vdscript(vdscript_filepath, fps, extra_frames)
    write_llc_file(llc_filepath, media_filename, cut_segments)

# Usage example
if __name__ == "__main__":
    vdscript_filepath = r"C:\New folder\test.vdscript"  # Path to the .vdscript file
    llc_filepath = r"C:\New folder\output.llc"  # Path to save the .llc file
    media_filename = "test.mp4"  # Name of the video file
    fps = ?  # Frame rate of the video - replace "?" with e.g., "23.976", "25" etc
    extra_frames = 16  # Number of frames to add to the end of each cut
    
    convert_vdscript_to_llc(vdscript_filepath, llc_filepath, media_filename, fps, extra_frames)
