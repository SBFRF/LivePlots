from MyLocalPlots import plotDataAvailablilty
import datetime as DT
start = DT.datetime(2020, 3, 15)
end = DT.datetime(2020, 6, 1)
days = (end - start).days
print('gathering data from {} to {}: {} days'.format(start, end, days ))
plotDataAvailablilty('/home/spike/repos/LivePlots/todaysDataStreams.yml',
     days=days, saveName='/home/spike/repos/LivePlots/dataAvailability_{}.png'.format(start.strftime("%Y_%m_%d")),
                     endTime=end)

start = DT.datetime(2018, 2, 10)
end = DT.datetime(2018, 3, 20)
days = (end - start).days
print('gathering data from {} to {}: {} days'.format(start, end, days ))
plotDataAvailablilty('/home/spike/repos/LivePlots/todaysDataStreams.yml',
     days=days, saveName='/home/spike/repos/LivePlots/dataAvailability_{}.png'.format(start.strftime("%Y_%m_%d")),
                     endTime=end)