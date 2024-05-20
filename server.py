"""
Server Script for Remote Mouse Control and Screen Sharing(Documentation)

This script establishes a server that allows remote clients to control the mouse
and view the screen of the server machine. It utilizes sockets for network communication,
PyAutoGUI for mouse control, MSS for screen capturing, and threading for handling
multiple clients concurrently.


Requirements:
- Python
- PyAutoGUI: https://pyautogui.readthedocs.io/en/latest/
- MSS: https://python-mss.readthedocs.io/en/stable/

Usage:
1. Run the script on the server machine.
2. Clients connect to the server using the appropriate IP address and port.
3. Clients provide a password for authentication.
4. Once authenticated, clients can control the server's mouse and view the screen.

Functions:
    handle_mouse_control(): To handle mouse controls based upon data sended by the client
    take_Screenshots(): For taking continous screenshots so that it becomes a videoe

Threads:
    Thread1: thread for handle_mouse_control function
    Thread2: thread for take_Screenshot function

"""


from socket import socket
from threading import Thread
from zlib import compress
import pyautogui
from mss import mss
import random
import string

WIDTH = 1920
HEIGHT = 1080



def handle_mouse_control(conn,addr):
    ctrl = False
 
    try:
        while True:
            msg = conn.recv(1024).decode()
            print(msg)
            if msg == 'stop':
                print(f"Client {addr} disconnected")
                break
            elif msg=='ctrl':
                ctrl=not ctrl
                
            
            # Interpret command and perform action
            elif msg == 'w':
                pyautogui.moveRel(0,-10, duration = 0.1)  # Move the mouse left by 10 pixels
            elif msg=='s' or msg=='S':
                pyautogui.moveRel(0, 10, duration = 0.1)
            elif msg=='a' or msg=='A':
                pyautogui.moveRel(-10, 0, duration = 0.1)
            elif msg=='d' or msg=='D':
                pyautogui.moveRel(10, 0, duration = 0.1)
            elif msg=='c' or msg=="C":
                pyautogui.click((pyautogui.position()[0],pyautogui.position()[1]))
            elif msg[:2]=="s " or msg[:2]=="S ":
                try:
                    pixel = int(msg[2:])
                    pyautogui.moveRel(0, pixel, duration = 0.01*(pixel//5))
                except:
                    pass
            elif msg[:2]=="w " or msg[:2]=="W ":
                try:
                    pixel = int(msg[2:])
                    pyautogui.moveRel(0, pixel*(-1), duration = 0.01*(pixel//5))
                except:
                    pass
            elif msg[:2]=="a " or msg[:2]=="A ":
                try:
                    pixel = int(msg[2:])
                    pyautogui.moveRel((-1)*pixel, 0, duration = 0.01*(pixel//5))
                except:
                    pass
            elif msg[:2]=="d " or msg[:2]=="D ":
                try:
                    pixel = int(msg[2:])
                    pyautogui.moveRel(pixel, 0, duration = 0.01*(pixel//5))
                except:
                    pass
            # conn.send("Message received from server".encode('utf-8'))
            else:
                if 'c' in msg and ctrl:
                    pyautogui.click((pyautogui.position()[0],pyautogui.position()[1]))
                try:
                    post=msg.split()
                    print(post)
                    pyautogui.moveTo((int(post[0]),int(post[1])))
                except:
                    pass


    finally:
        conn.close()

def take_Screenshots(conn):
    with mss(with_cursor=True) as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while True:
                
                
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb,6)

            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Send pixels
            conn.sendall(pixels)

def main(host='172.31.39.43', port=5205):
    sock = socket()
    sock.bind((host, port))
    

    try:
        sock.listen(5)
        # print("Server listening on port", port)
        print("Server has ip address of ",host)
        print("And is listening on the port ",port)
        unlocked=False
        



        # Define the characters you want to include in the random string
        characters = string.ascii_letters + string.digits

        # Generate a random string of length 4
        password = ''.join(random.choices(characters, k=4))

        print(password)



        while True:
            conn, addr = sock.accept()
            print('Client connected IP:', addr)

            msg = conn.recv(1024).decode()
            print(msg,password)
            
            if msg==password:
                # sock.sendall("User verified".encode())
                unlocked=True
            
            else:
                print("Wrong password entered by the client")
                print("Restarting the server")
                break

                
            
            if unlocked:
                print("Client verified")
              
            # Start a separate thread for handling mouse control
                mouse_thread = Thread(target=handle_mouse_control, args=(conn,addr))
                mouse_thread.start()
            
                # Start another thread for screen sharing
                screen_thread = Thread(target=take_Screenshots, args=(conn,))
                screen_thread.start()


                mouse_thread.join()
                screen_thread.join()


    finally:
        sock.close()
        if not unlocked:
            port+=1
            main(host=host,port=port)

if __name__ == '__main__':
    main()
