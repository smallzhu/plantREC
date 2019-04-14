#coding = utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
class recongnition:
    file_name = ""
    model_file = ""
    label_file = ""
    def __init__(self,file_name,model_file,label_file):
        self.file_name = file_name
        self.model_file = model_file
        self.label_file = label_file

    def load_graph(self):
        graph = tf.Graph()
        graph_def = tf.GraphDef()
        with open(self.model_file,"rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)
        return graph

    def read_tensor_from_image_file(self):
        input_name = "file_reader"
        output_name = "normalized"
        file_reader = tf.read_file(self.file_name, input_name)

        if self.file_name.endswith(".png"):
            image_reader = tf.image.decode_png(file_reader, channels=3, name="png_reader")
        elif self.file_name.endswith(".gif"):
            image_reader = tf.squeeze(tf.image.decode_gif(file_reader, name="gif_reader"))
        elif self.file_name.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
        else:
            image_reader = tf.image.decode_jpeg(file_reader, channels=3, name="jpeg_reader")
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [299, 299])
        normalized = tf.divide(tf.subtract(resized, [0]), [255])
        sess = tf.Session()
        result = sess.run(normalized)

        return result

    def load_labels(self):
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(self.label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label

