#!/usr/bin/env python3
import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'
    
    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)
    graph = tf.get_default_graph()
    w1 = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3 = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4 = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7 = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)    
    
    return w1, keep, layer3, layer4, layer7

tests.test_load_vgg(load_vgg, tf)

print("Load OK");

def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer3_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer7_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    pool7_conv_1x1 = tf.layers.conv2d(vgg_layer7_out, num_classes, 1, strides= (1, 1), padding='same', kernel_initializer = tf.random_normal_initializer(stddev=0.01),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(0.0001))
    output_32x = tf.layers.conv2d_transpose(pool7_conv_1x1, num_classes, 4, strides= (2, 2), padding='same', kernel_initializer = tf.random_normal_initializer(stddev=0.01),
                                       kernel_regularizer=tf.contrib.layers.l2_regularizer(0.0001))
    
    pool4_conv_1x1 = tf.layers.conv2d(vgg_layer4_out, num_classes, 1, strides= (1, 1), padding='same', kernel_initializer = tf.random_normal_initializer(stddev=0.01),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(0.0001))  
    pool4_skip = tf.add(output_32x, pool4_conv_1x1)
    output_16x = tf.layers.conv2d_transpose(pool4_skip, num_classes, 4, strides= (2, 2), padding='same', kernel_initializer = tf.random_normal_initializer(stddev=0.01),
                                       kernel_regularizer=tf.contrib.layers.l2_regularizer(0.0001))
    
    pool3_conv_1x1 = tf.layers.conv2d(vgg_layer3_out, num_classes, 1, strides= (1, 1), padding='same', kernel_initializer = tf.random_normal_initializer(stddev=0.01),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(0.0001))  
    pool3_skip = tf.add(output_16x, pool3_conv_1x1)
    output_8x = tf.layers.conv2d_transpose(pool3_skip, num_classes, 16, strides= (8, 8), padding='same', kernel_initializer = tf.random_normal_initializer(stddev=0.01),
                                       kernel_regularizer=tf.contrib.layers.l2_regularizer(0.0001))  
        
    #tf.Print(output_8x, [tf.shape(output_8x[1:3])])
        
    return output_8x

tests.test_layers(layers)
print("test_layers OK");

def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    label = tf.reshape(correct_label, (-1,num_classes))
    
    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits= logits, labels= label))    
    optimizer = tf.train.AdamOptimizer(learning_rate= learning_rate)    
    train_op = optimizer.minimize(cross_entropy_loss)
    
    prediction = tf.argmax(nn_last_layer, axis=3)
    ground_truth = correct_label[:, :, :, 0]
    mean_iou, update_op = tf.metrics.mean_iou(ground_truth, prediction, num_classes)
    iou = (mean_iou, update_op)    
    
    return logits, train_op, cross_entropy_loss, iou

#tests.test_optimize(optimize)
print("test_optimize OK");

def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate, iou):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function   
    sess.run(tf.global_variables_initializer())
    sess.run(tf.local_variables_initializer())
    
    loss_list = []
    iou_list = []
    
    for epoch in range(epochs):
        print('Epoch : {}'.format(epoch + 1))
        loss_data = []
        total_iou = 0.0
        image_cnt = 0
        loss = 0.0
        
        for image, label in get_batches_fn(batch_size):
            #print("\n\nTraining image shape = {}".format(tf.shape(image)))
            #print("\nTraining label shape = {}".format(tf.shape(label)))
            _, loss = sess.run([train_op, cross_entropy_loss], feed_dict={input_image: image, correct_label: label, keep_prob: 0.5, learning_rate: 0.0001})
            loss_data.append(loss)
            image_cnt+=len(image)       
        
            m_iou = iou[0]
            op_iou = iou[1]
            sess.run(op_iou, feed_dict={input_image: image, correct_label: label, keep_prob: 1.0})
            mean_iou = sess.run(m_iou)
            total_iou += mean_iou * len(image)
            
        average_iou = total_iou / image_cnt    
        print("Loss : {:.6f}".format(loss))
        print("IoU : {:.6f}".format(average_iou))
        loss_list.append(loss)
        iou_list.append(average_iou)
    print(loss_list)
    print(iou_list)

#tests.test_train_nn(train_nn)
print("test_train_nn OK");

def run():
    num_classes = 2
    image_shape = (160, 576)  # KITTI dataset uses 160x576 images
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)
    print("test_for_kitti_dataset ok");
    
    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)
    print("maybe_download_pretrained_vgg ok");
    
    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/
    
    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        input_image, keep_prob, layer3_out, layer4_out, layer7_out = load_vgg(sess, vgg_path)
        layer_output = layers(layer3_out, layer4_out, layer7_out, num_classes)
        
        correct_label = tf.placeholder(tf.int32, [None, None, None, num_classes], name='correct_label')
        learning_rate = tf.placeholder(tf.float32, name='learning_rate')
        iou = None        

        logits, train_op, cross_entropy_loss, iou = optimize(layer_output, correct_label, learning_rate, num_classes)

        # TODO: Train NN using the train_nn function
        epochs = 50
        batch_size = 2        
        
        train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image, correct_label, keep_prob, learning_rate, iou)
        
        # TODO: Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)        
        
        # OPTIONAL: Apply the trained model to a video


if __name__ == '__main__':
    run()
