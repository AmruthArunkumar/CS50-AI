- trial 1: same variable values as shown in the lecture 
  (max training accuracy: 5.62%)
- trial 2: since low accuracy, decreased dropout by 0.2 
  (max training accuracy: 5.69%)
- trial 3: since there was a small change, I kept 0.3 dropout and 
  added a hidden layer identical to one before 
  (max training accuracy: 5.84%)
- trial 4: not much change, so kept 1 hidden layer, and added another
  convolutional and pooling layer (max training accuracy: 88.69%)
- trial 5: huge increase because of second convolutional and
  pooling layer. just wanted to see what would happen if I
  removed the input type from the second convolutional layer 
  (max training accuracy: 90.80%)
- trial 6: slight increase, but am not sure why, so I am 
  deciding to put back the input type parameter and 
  going to make the pool size for the second layer 3x3
  (max training accuracy: 91.27%)
- trial 7: little increase so going to keep this change, 
  and I am going to increase the second convolutional layer
  filter size to 4x4 (max training accuracy: 81.53%)
- trial 8: since increasing filter size lowered accuracy 
  I am going to lower filter size to 2x2 
  (max training accuracy: 89.06%)
- trial 9: lowering filter size doesn't seem to increase 
  accuracy, so I'm going to keep 3x3. I am going to change 
  the first value of the number of filters to 16
  (max training accuracy: 90.88%)
- trial 10: there was an increase in accuracy, so going to 
  try changing first activation function to sigmoid
  (max training accuracy: 93.94%)
- tried more changes and finally got one with a 
  96.43% max training accuracy and 97.48% testing accuracy
-
-
