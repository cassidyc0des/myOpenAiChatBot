# OpenAI ChatBot

This is an example chat bot someone could create using OpenAi gpt-3.5-turbo model.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)

## Features

- Front End HTML: Simple and cute chatbot HTML/CSS/JS
- OpenAI Responses: Direct connection to the open source gpt-3.5-turbo model
- Lucio!: Right now I just thought it would be fun to make the chat bot act like Lucio from Overwatch. 

## Installation

### Prerequisites

- Python
- OpenAI Key
- Django

### Installation Steps

1. Clone the repository:
    ```sh
    git clone https://github.com/cassidyc0des/myOpenAiChatBot.git
    cd myOpenAiChatBot
    ```

2. Install dependencies:
    If you don't have pip follow documentation on how to install pip.
    Then...
    ```sh
    - pip install python
    - pip install openai
    - pip install django
    ```
    You may need to set up a Virtual Environment.

4. Set up environment variables:
    ```sh
    cp .env.example .env
    # Edit .env file to add your API keys or other configuration settings
    ```

5. Start the application:
    Once all is installed simply navigate to chatbot_project
    ```sh
    cd chatbot_project
    python manage.py runserver
    ```

## Usage

1. Open your browser and go to `http://localhost:3000`.
2. Type into the text box anything, press enter or send. 

### Screenshots

![ScreenRecording2024-07-23at3.59.09PM-ezgif.com-video-to-gif-converter.gif](https://images.squidge.org/images/2024/07/23/ScreenRecording2024-07-23at3.59.09PM-ezgif.com-video-to-gif-converter.gif)
