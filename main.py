from datetime import datetime
from os import mkdir, path
import requests
from tkinter import *
from tkinter import filedialog

bgc = '#FAEFEA'

def logging(message):
    print(str(datetime.now()) + ' - ' + message)


def send_request(request_url):
    response = requests.get(request_url)
    return response.status_code, response.json()


TKroot = Tk()
TKroot.title("=)")
userChat = BooleanVar()
membersOnly = BooleanVar()
getPhotos = BooleanVar()
getVideos = BooleanVar()
accessToken = StringVar()
peerId = StringVar()
offset = IntVar()
folder = StringVar()

def main():
    TKroot.resizable(width = None, height = None)
    TKroot.minsize(360, 270)
    TKroot.columnconfigure(0, weight=1)
    TKroot.rowconfigure(0, weight=1)
    root = Frame(TKroot, bg = bgc)
    root.grid(sticky=E+W+S+N)

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1)
    root.rowconfigure(4, weight=1)
    root.rowconfigure(5, weight=1)
    root.rowconfigure(6, weight=1)
    root.rowconfigure(7, weight=1)
    root.rowconfigure(8, weight=2)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=5)

    Label(root, text="Access token:", bg = bgc).grid(row=0, sticky=E+W+S+N)
    Label(root, text="Peer id:", bg = bgc).grid(row=1, sticky=E+W+S+N)
    Label(root, text="Offset:", bg = bgc).grid(row=2, sticky=E+W+S+N)

    tokenEntry = Entry(root, bg = bgc, textvariable=accessToken)
    tokenEntry.grid(row=0, column=1, sticky=E+W+S+N)
    
    peerEntry = Entry(root, bg = bgc, textvariable = peerId)
    peerEntry.grid(row=1, column=1, sticky=E+W+S+N)
    
    offsetEntry = Entry(root, bg = bgc, textvariable = offset)
    offsetEntry.grid(row=2, column=1, sticky=E+W+S+N)

    userChatButton = Checkbutton(root, text = 'User chat   ', bg = bgc, variable = userChat, anchor = W)
    userChatButton.grid(row = 3, column = 1, sticky = E+W+S+N)
    
    membersOnlyButton = Checkbutton(root, text = 'Members only   ', bg = bgc, variable = membersOnly, anchor = W, justify = LEFT)
    membersOnlyButton.grid(row = 4, column = 1, sticky = E+W+S+N)
    
    getPhotosButton = Checkbutton(root, text = 'Photos   ', bg = bgc, variable = getPhotos, anchor = W, justify = LEFT)
    getPhotosButton.grid(row = 5, column = 1, sticky = E+W+S+N)
    
    getVideosButton = Checkbutton(root, text = 'Videos   ', bg = bgc, variable = getVideos, anchor = W, justify = LEFT)
    getVideosButton.grid(row = 6, column = 1, sticky = E+W+S+N)

    selectFolderButton = Button(root, text="Select folder", bg = bgc, command=selectDirectory)
    selectFolderButton.grid(row = 7, column = 0, columnspan = 2, sticky = E+W+S+N)

    downloadButton = Button(root, text="Download", command=download, bg = bgc)
    downloadButton.grid(row=8, column=0, columnspan = 2, sticky=E+W+S+N)

    TKroot.mainloop()

def download():
    get(accessToken=accessToken.get(), peerId=peerId.get(), downloadPhotos=getPhotos.get(), downloadVideos=getVideos.get(), userChat=userChat.get(), membersOnly=membersOnly.get())

def selectDirectory():
    filename = filedialog.askdirectory()
    folder.set(filename + '/')

def get(accessToken = '', peerId = '', downloadPhotos = False, downloadVideos = False, userChat = False, membersOnly = False):
    api_version = '5.103'
    user_url = 'https://api.vk.com/method/users.get?v=%s&access_token=%s&user_ids=' % (api_version, accessToken)
    chat_url = 'https://api.vk.com/method/messages.getChat?v=%s&access_token=%s&chat_id=' % (api_version, accessToken)
    photos_url = 'https://api.vk.com/method/messages.getHistoryAttachments?v=%s&access_token=%s&media_type=photo&peer_id=' % (
    api_version, accessToken)
    videos_url = 'https://api.vk.com/method/messages.getHistoryAttachments?v=%s&access_token=%s&media_type=video&peer_id=' % (
    api_version, accessToken)
    if userChat:
        status, response = send_request(user_url + peerId)
        if status == 200:
            download_folder = response['response'][0]['first_name'] + ' ' + response['response'][0]['last_name']
    else:
        status, response = send_request(chat_url + peerId)
        peerId = str(int(peerId) + 2000000000)
        if status == 200:
            member_list = response['response']['users']
            download_folder = response['response']['title']
    download_folder = folder.get() + download_folder
    if not path.exists(download_folder):
        mkdir(download_folder)
    download_folder = download_folder + '/'
    if downloadPhotos:
        running = True
        start_from = ''
        i = offset.get()
        while running:
            status, response = send_request(photos_url + peerId + start_from)
            if status == 200:
                data = response['response']
                if 'next_from' in data:
                    items = data['items']
                    for item in items:
                        id = [item['from_id']]
                        
                        if (userChat and ((not membersOnly) or (id == peerId))) or (not userChat and ((not membersOnly) or (set(id) & set(member_list) != set()))):
                            if i > 0:
                                i = i - 1
                                continue
                            photo = item['attachment']['photo']['sizes']
                            photo_url = max(photo, key=lambda x:x['width'])['url']
                            date = item['attachment']['photo']['date']
                            value = datetime.fromtimestamp(date)
                            str_date = value.strftime('%Y-%m-%d_%H:%M:%S')
                            filename = photo_url.split('.')[-1]
                            r = requests.get(photo_url)
                            if r.status_code == 200:
                                open(download_folder + str_date + '.' + filename, 'wb').write(r.content)
                                logging('Photo downloaded!')
                            else:
                                logging('Failed to download!')
                    start_from = '&start_from=' + data['next_from']
                else:
                    running = False
            else:
                logging('Error ' + str(status))
    logging('Photos download complete!')
    if downloadVideos: 
        running = True
        start_from = ''
        i = offset.get()
        while running:
            status, response = send_request(videos_url + peerId + start_from)
            if status == 200:
                data = response['response']
                if 'next_from' in data:
                    items = data['items']
                    for item in items:
                        id = [item['attachment']['video']['owner_id']]
                        if (userChat and ((not membersOnly) or (id == peerId))) or (not userChat and ((not membersOnly) or (set(id) & set(member_list) != set()))):
                            if i > 0:
                                i = i - 1
                                continue
                            video = item['attachment']['video']['files']
                            if not ('mp4_240' in video):
                                continue
                            video_url = video[list(video.keys())[-2]]
                            date = item['attachment']['video']['date']
                            value = datetime.fromtimestamp(date)
                            str_date = value.strftime('%Y-%m-%d_%H:%M:%S')
                            filename = video_url.split('.')[-1].split('?')[0]
                            r = requests.get(video_url)
                            if r.status_code == 200:
                                open(download_folder + str_date + '.' + filename, 'wb').write(r.content)
                                logging('video downloaded!')
                            else:
                                logging('Failed to download!')
                    start_from = '&start_from=' + data['next_from']
                else:
                    running = False
            else:
                logging('Error ' + str(status))
    logging('Videos download complete!')
    

if __name__ == "__main__":
    main()
    print("Done")