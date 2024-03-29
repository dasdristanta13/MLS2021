# -*- coding: utf-8 -*-
"""HW_Dristanta_Das.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rH2_uyzaCdOTyPdB2XoY5YtApAwMlvFg
"""

!git clone https://github.com/YoongiKim/CIFAR-10-images

!ls

!pwd

# !cd CIFAR-10-images/

!ls

import torch
import numpy as np
from __future__ import print_function, division
import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import cv2
from skimage import io, transform
from PIL import Image
from sklearn.model_selection import train_test_split
import torch.optim as optim


# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

# check if CUDA is available
train_on_gpu = torch.cuda.is_available()

if not train_on_gpu:
    print('CUDA is not available.  Training on CPU ...')
else:
    print('CUDA is available!  Training on GPU ...')

def load_images(train_path,test_path):
  train_classes = os.listdir(train_path)
  test_classes = os.listdir(test_path)

  train_images = []
  test_images = []

  print("Loading Train Images")
  for cls in train_classes:
    print("Reading images of class: ", cls)
    cls_path = os.path.join(train_path, cls)
    for img_id in os.listdir(cls_path):
      img = cv2.imread(os.path.join(cls_path, img_id))
      # img=img/255
      #img=img.astype("float32")
      train_images.append([img, cls])

  print("Loading Test Images")
  for cls in test_classes:
    print("Reading images of class: ", cls)
    cls_path = os.path.join(test_path, cls)
    for img_id in os.listdir(cls_path):
      img = cv2.imread(os.path.join(cls_path, img_id))
      # img= img/255
      #img=img.astype("float32")
      test_images.append([img, cls])
  
  return  train_images,test_images



train_path = '/content/CIFAR-10-images/train'
test_path = '/content/CIFAR-10-images/test'

train_images ,test_images= load_images(train_path,test_path)
train_images, valid_images = train_test_split(train_images, test_size = 0.2)
print(len(train_images), len(test_images), len(valid_images))

os.listdir('/content/CIFAR-10-images/train')

class CifarDataset(Dataset):
    def __init__(self, images, transform=None):
        '''
        Args : 
            csvfile : train/val/test csvfiles
            audio_dir : directory that contains folders 0 - f
        '''
        self.images = images
        self.transform = transform

    # get one segment (==59049 samples) and its 50-d label
    def __getitem__(self, index):

      if self.transform:
        x = torch.tensor(self.transform(Image.fromarray(self.images[index][0]))).to(torch.float32)
      else:
        x = torch.tensor(Image.fromarray(self.images[index][0])).to(torch.float32)
      y = self.images[index][1]

      sample = {'image': x, 'class': y}



      return sample

        
    
    def __len__(self):
        return len(self.images)


transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])


train_data = CifarDataset(train_images,transform=transform_train)
test_data = CifarDataset(test_images,transform=transform_test)
valid_data = CifarDataset(valid_images,transform=transform_train)

print(len(train_data), len(test_data),len(valid_data))


trainloader = torch.utils.data.DataLoader(
    train_data, batch_size=20, shuffle=True, num_workers=2)
validloader = torch.utils.data.DataLoader(valid_data, batch_size=20,shuffle=True, num_workers=2)
testloader = torch.utils.data.DataLoader(
    test_data, batch_size=20, shuffle=False, num_workers=2)

for i in trainloader:
  img=i['image'][10][0]
  cls=i['class'][10]
  plt.imshow(img)
  plt.show()
  print(cls)

trainloader

import torch.nn as nn
import torch.nn.functional as F

# define the CNN architecture
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # convolutional layer (sees 32x32x3 image tensor)
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        # convolutional layer (sees 16x16x16 tensor)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        # convolutional layer (sees 8x8x32 tensor)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        # max pooling layer
        self.pool = nn.MaxPool2d(2, 2)
        # linear layer (64 * 4 * 4 -> 500)
        self.fc1 = nn.Linear(64 * 4 * 4, 500)
        # linear layer (500 -> 10)
        self.fc2 = nn.Linear(500, 10)
        # dropout layer (p=0.25)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        # add sequence of convolutional and max pooling layers
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        # flatten image input
        x = x.view(-1, 64 * 4 * 4)
        # add dropout layer
        x = self.dropout(x)
        # add 1st hidden layer, with relu activation function
        x = F.relu(self.fc1(x))
        # add dropout layer
        x = self.dropout(x)
        # add 2nd hidden layer, with relu activation function
        x = self.fc2(x)
        return x

class_dict = {'bird':0,
 'cat':1,
 'dog':2,
 'automobile':3,
 'horse':4,
 'frog':5,
 'ship':6,
 'deer':7,
 'airplane':8,
 'truck':9}

for i, sample in enumerate(trainloader):
  print(sample['class'])
  data_y = []
  for cls in sample['class']:
    data_y.append(class_dict[cls])
  print(data_y)

  break

# number of epochs to train the model
device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
model = Net().to(device)
n_epochs = 110

optimizer = optim.SGD(model.parameters(), lr = 0.001)
criterion = nn.CrossEntropyLoss()



valid_loss_min = np.Inf # track change in validation loss
for epoch in range(1, n_epochs+1):
    print("Train Epoch: ", epoch)

    # keep track of training and validation loss
    train_loss = 0.0
    valid_loss = 0.0
    
    ###################
    # train the model #
    ###################
    model.train()
    for sample in trainloader:
        batch_x = sample['image'].to(device)
        # batch_y =np.zeros((128,10)).astype('int')
        batch_y = []
        for i, cls in enumerate(sample['class']):
          # batch_y[i][class_dict[cls]] = 1 
          batch_y.append(class_dict[cls])
        batch_y = torch.tensor(batch_y).to(device)
        # print(batch_y.tolist())

        output = model(batch_x)
        # move tensors to GPU if CUDA is available
        # if train_on_gpu:
        #     data, target = data.cuda(), target.cuda()
        # clear the gradients of all optimized variables
        optimizer.zero_grad()
        # forward pass: compute predicted outputs by passing inputs to the model
        # output = model(data)
        # calculate the batch loss
        #print(batch_y[0])
        #print(output[0])
        loss = criterion(output, batch_y)
        # backward pass: compute gradient of the loss with respect to model parameters
        loss.backward()
        # perform a single optimization step (parameter update)
        optimizer.step()
        # update training loss
        train_loss += loss.item()
        
    ######################    
    # validate the model #
    ######################
    # model.eval()
    for sample in validloader:
        batch_x = sample['image'].to(device)
        batch_y = []
        for cls in sample['class']:
          batch_y.append(class_dict[cls])
        batch_y = torch.tensor(batch_y).to(device)


        # forward pass: compute predicted outputs by passing inputs to the model
        output = model(batch_x)
        # calculate the batch loss
        
        loss = criterion(output, batch_y)
        # update average validation loss 
        valid_loss += loss.item()
    
  
        
    # print training/validation statistics 
    print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
        epoch, train_loss, valid_loss))
    
    #save model if validation loss has decreased
    if valid_loss <= valid_loss_min:
        print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
        valid_loss_min,
        valid_loss))
        torch.save(model.state_dict(), 'model_cifar.pt')
        valid_loss_min = valid_loss

# track test loss
test_loss = 0.0
# class_correct = list(0. for i in range(10))
# class_total = list(0. for i in range(10))
actual=[]
predict=[]



model.eval()
# iterate over test data
for sample in testloader:
  batch_x = sample['image'].to(device)
  batch_y = []
  for cls in sample['class']:
    batch_y.append(class_dict[cls])
  batch_y = torch.tensor(batch_y).to(device)
  #print(batch_y.tolist())
  output = model(batch_x)
  #print(batch_x)
    # calculate the batch loss
  loss = criterion(output, batch_y)
    # update test loss 
  test_loss += loss.item()
    # convert output probabilities to predicted class
  _, pred = torch.max(output, 1)    
    # compare predictions to true label
  correct_tensor = pred.eq(batch_y.data.view_as(pred))
  #print(correct_tensor)
  correct = np.squeeze(correct_tensor.numpy()) if not train_on_gpu else np.squeeze(correct_tensor.cpu().numpy())
  for i in correct:
    predict.append(i)
  for j in  batch_y.tolist():
    actual.append(j)

(sum(predict)/len(predict))*100

