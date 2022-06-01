import os
import numpy as np
import rosbag
import sys

class RosBagSplitter(object):
    '''Splits the input bag into multiple small bags. Cares about provided topic.'''
    def __init__(self, inbag, topic_name, empty_time, outfile_prefix, outdir):
        self.inbag = inbag
        self.outfile_prefix = outfile_prefix
        self.outdir = outdir
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.topic_name = topic_name
        self.splitting_times = []
        self.empty_time = empty_time

    def identify_splits(self):
        self.bag = rosbag.Bag(self.inbag)
        self.messages = self.bag.read_messages(topics=self.topic_name)
        print("Identifying splits for topic name", self.topic_name)
        print(self.messages)
        last_time = 0
        i= 0
        for topic, msg, t in self.messages:
            if i == 0:
                last_time = t.to_sec()
                i = i+1
                self.splitting_times.append(last_time)
                continue
            
            if t.to_sec()-last_time>self.empty_time:
                self.splitting_times.append(last_time)
                self.splitting_times.append(t.to_sec())
                
            last_time = t.to_sec()
        self.splitting_times.append(last_time)
        print("Splitting times:")
        print(self.splitting_times)

    def split(self):
        '''Splits a bag into multiple bags'''
        self.identify_splits()
        self.gen = self.bag.read_messages()
        j = 1
        for i in range(0,len(self.splitting_times)-1,2):
            outbag = self.outfile_prefix + str(j) + '.bag' 
            outbag = os.path.join(self.outdir, outbag)
            print("extracting bag:",outbag)
            print("start:",self.splitting_times[i])
            print("stop:",self.splitting_times[i+1])
            self.extract(self.splitting_times[i], self.splitting_times[i+1], outbag=outbag)
            j = j + 1
            

    def extract(self, msg_start, msg_end, outbag=None):
        '''Extracts one chunk of all topics between [msg_start, msg_end)'''
        assert msg_start >=0 and msg_start < msg_end, 'Hmmm.. something is not right in the args you passed'
 
        if outbag is None:
            outbag = self.outfile_prefix + str(msg_start) + str(msg_end)
            outbag = os.path.join(self.outdir, outbag)
        with rosbag.Bag(outbag, 'w') as f:
            previous_state = False
            for topic, msg, t in self.gen:
                capture = t.to_sec() >= msg_start and t.to_sec() <= msg_end
                if not capture and previous_state!=capture:
                    break
                previous_state = capture
                if capture:
                    f.write(topic, msg, t)

    

# entry to main land
if __name__=='__main__':
    if len(sys.argv) < 3:
        print('Usage: ', sys.argv[0], ' ', 'dataset.bag topic_name (empty_time)')
        sys.exit(1)
    inbag = sys.argv[1]
    topic_name = sys.argv[2]
    empty_time = 3
    if len(sys.argv) == 4:
        empty_time = int(sys.argv[3])
    
    base = os.path.splitext(os.path.basename(inbag))[0]
    # create a splitter
    splitter = RosBagSplitter(inbag, topic_name, empty_time, outfile_prefix=base+'_small_', outdir=base+'_split_bags')
    splitter.split()