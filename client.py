"""
Client Script for Remote Mouse Control and Screen Viewing(Documentation)

This script connects to a remote server to control the mouse and view the screen
of the server machine. It utilizes sockets for network communication, Pygame for
screen display, PyAutoGUI for mouse control, and threading for concurrent tasks.

Requirements:
- Python 
- Pygame: https://www.pygame.org/docs/
- PyAutoGUI: https://pyautogui.readthedocs.io/en/latest/
- pynput: https://pypi.org/project/pynput/

Usage:
1. Run the script on the client machine.
2. Enter the IP address and port of the remote server.
3. Provide the password for authentication.
4. Once authenticated, control the server's mouse and view the screen.

Functions:
    recvall(): a function to retrieve all pixels based on length sended 
    send_mouse_commands(): To send mouse commands to the server
    retreive_screenshot():to retrieve screenshots from the server and display them
    position_fun(): send mouse positions to the server
    on_click(): callback function for mouse click events

Threads:
    Thread1: for send_mouse_commands function
    Thread2: for retreive_screenshot function
    Thread3: for position_funt function
    Thread4: for on_click funt function
"""



from socket import socket
from threading import Thread
from zlib import decompress
import pygame
import pyautogui
import time
from pynput import mouse

WIDTH = 1920
HEIGHT = 1080
ctrl = False
clicked = False

def recvall(conn, length):
    """ Retrieve all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def send_mouse_commands(conn):
    global ctrl
    try:
        while True:
            command=input("Enter the command (type 'stop' to disconnect, 'ctrl' to acquire/release server's mouse control):").strip()
            if command=="ctrl":
                ctrl = not ctrl
            conn.sendall(command.encode())

            if command=='stop':
                break

    finally:
        conn.close()

def retreive_screenshot(conn):
    info = pygame.display.Info()  # Get display information
    W = info.current_w  # Get current screen width
    H = info.current_h  # Get current screen height
    print(W)
    print(H)

    screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
    clock = pygame.time.Clock()
    watching = True
    
    try:    
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break

            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(conn.recv(1), byteorder='big')
            size = int.from_bytes(conn.recv(size_len), byteorder='big')
            pixels = decompress(recvall(conn, size))

            # Create the Surface from raw pixels
            img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

            # Display the picture
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(60)
    finally:
        conn.close()

def position_fun(conn):
    global ctrl,clicked
    while True:
        if ctrl:
            if clicked:
                command="c"
                conn.sendall(command.encode())
            clicked = False
            post=str(pyautogui.position()[0])+" "+str(pyautogui.position()[1])
            conn.sendall(post.encode())
        time.sleep(0.1)

def on_click(x, y, button, pressed):
    global clicked
    if button == mouse.Button.left:
        if pressed:
            clicked=True
            return True

def main(host='172.31.39.43', port=5208):
    sock = socket()
    sock.connect((host, port))
    try:
        pwd = input("Connection established. Enter password:")
        sock.sendall(pwd.encode())
        # Start a separate thread for handling mouse control
        mouse_thread = Thread(target=send_mouse_commands, args=(sock,))
        mouse_thread.start()

        # Start another thread for screen sharing
        screen_thread = Thread(target=retreive_screenshot, args=(sock,))
        screen_thread.start()

        position_thread=Thread(target=position_fun,args=(sock,))
        position_thread.start()

        listener = mouse.Listener(on_click=on_click)
        listener.start()
        listener.join()

        mouse_thread.join()
        screen_thread.join()
        position_thread.join()

    finally:
        sock.close()

if __name__ == '__main__':
    pygame.init()
    port = int(input("Enter port number:"))
    main(port=port)