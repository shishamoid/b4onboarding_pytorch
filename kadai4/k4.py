import torch
import torch.nn as nn
from torch import optim
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import numpy as np
import matplotlib.pyplot as plt
import os
import math


def dataload():
    r = 2  # 半径

    θ = np.linspace(0, 2*math.pi, num=50)

    correct_x = []
    correct_y = []

    for i in range(len(θ)):
        correct_x.append(r*math.cos(θ[i]))
        correct_y.append(r*math.sin(θ[i]))

    input_data = []
    correct_data = []

    for i in range(len(correct_x)):
        if i == (len(correct_x)-1):
            input_data.append([correct_x[i], correct_y[i]])
            correct_data.append([correct_x[0], correct_y[0]])
        else:
            input_data.append([correct_x[i], correct_y[i]])
            correct_data.append([correct_x[i+1], correct_y[i+1]])

    input_data = torch.FloatTensor(input_data)
    correct_data = torch.FloatTensor(correct_data)

    dataset = TensorDataset(input_data, correct_data)
    train_loader = DataLoader(dataset, batch_size=8, shuffle=False)

    return input_data, train_loader


class feedforward(nn.Module):
    def __init__(self):
        super(feedforward, self).__init__()
        self.l1 = nn.Linear(2, 64)
        self.a1 = nn.ReLU()
        self.l2 = nn.Linear(64, 64)
        self.a2 = nn.ReLU()
        self.l3 = nn.Linear(64, 2)
        self.a4 = nn.ReLU()

    def forward(self, x):

        x = self.l1(x)
        h = self.a1(x)
        h = self.a1(self.l2(h))
        y = self.l3(h)
        return y


def train(train_loader, device, num_epoch):
    model = feedforward().to(device)

    loss_list = []
    epoch_list = []

    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    for i in range(num_epoch):

        model.train()
        loss_train = 0
        for j, xy in enumerate(train_loader):

            xy[0] = xy[0].to(device)
            xy[1] = xy[1].to(device)

            loss = criterion(model(xy[0]), xy[1])
            loss_train += loss.item()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        loss_train /= j+1

        loss_list.append(loss_train)
        epoch_list.append(i)
        if i % 10 == 0:
            print("Epoch:", i, "Loss_Train:", loss_train)

        if i % 50 == 0:
            print("save", i)
            torch.save(model.to('cpu').state_dict(),
                       './forward_models/epoch_{}_model.pth'.format(i))
            model.to(device)

    torch.save(model.to('cpu').state_dict(),
               './forward_models/last_epoch_{}_model.pth'.format(num_epoch))
    return model, loss_list, epoch_list


def draw_circle(model, pre):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    pre = pre.to(device)
    result_x = []
    result_y = []

    model = model.to(device)

    result = model(pre.unsqueeze(1)[0])#最初だけモデルに入力
    #result = result.cpu()
    result_x.append(result[0][0])
    result_y.append(result[0][1])

    count = 0
    while True:
        result = model(result.unsqueeze(1)[0])#クローズドループに変更
        #result = result.cpu()
        result_x.append(result[0][0])
        result_y.append(result[0][1])
        count +=1
        if count==50:
            break

    #円プロット用
    circle_x=[]
    circle_y=[]
    for i in range(50):
        circle_x.append(pre[i][0])
        circle_y.append(pre[i][1])

    fig = plt.figure()
    plt.plot(result_x, result_y, linestyle="None", linewidth=0, marker='o')
    plt.plot(circle_x, circle_y)
    plt.axes().set_aspect('equal', 'datalim')
    fig.savefig("./forward_pictures/forward_circle.png")

def main():
    os.makedirs("./forward_pictures", exist_ok=True)
    os.makedirs("./forward_models", exist_ok=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_data, traindata = dataload()
    model, loss_list, epoch_list = train(traindata, device, 100)
    draw_circle(model, input_data)

    fig = plt.figure()
    plt.plot(epoch_list, loss_list)
    #plt.axes().set_aspect('equal', 'datalim')
    fig.savefig("./forward_pictures/loss_forward.png")


if __name__ == '__main__':
    main()
