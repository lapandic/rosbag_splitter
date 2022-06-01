# rosbag_splitter
Rosbag splitter is useful for splitting bag files containing multiple experiments when the topic of interest is not being published for at least some known time (empty_time).

## Usage

`python rosbag_splitter.py input.bag  topic_name empty_time `

`empty_time` is an optional argument (default = 3 sec)

## Based on:
https://github.com/vnaveen9296/bag_splitter
