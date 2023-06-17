# Requirements Installation

1. Go to the directory containing this README file
2. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements

    ```bash
    pip install -r requirements.txt
    ```

# Running the Code

## In case the server is to be running on the same machine as the client:

<br/>

1. Run the python script of the server
    <div><ins>For Windows OS:</ins></div>

    ```bash
    python gameServer.py
    ```
    <div><ins>For Linux OS:</ins></div>

    ```bash
    python3 gameServer.py
    ```

2. Change the value of the variable "isServerLocal" to True

    ```python
    isServerLocal = True
    ```

3. Run the python script of the client
    <div><ins>For Windows OS:</ins></div>

    ```bash
    python gameClient.py
    ```
    <div><ins>For Linux OS:</ins></div>

    ```bash
    python3 gameClient.py
    ```

<br/>

## In case the server is running on the remote VM:

<br/>

1. Change the value of the variable "isServerLocal" to False

    ```python
    isServerLocal = False
    ```

2. Run the python script of the client
    <div><ins>For Windows OS:</ins></div>

    ```bash
    python gameClient.py
    ```
    <div><ins>For Linux OS:</ins></div>

    ```bash
    python3 gameClient.py
    ```

<br/>

# YouTube Video Link

https://youtu.be/pPPzZT7jt1U