FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libxcb-xinerama0 \
    libfontconfig1 \
    libxkbcommon-x11-0 \
    libxrender1 \
    libglib2.0-0 \          
    libdbus-1-3 \           
    libsm6 \                
    libice6 \               
    libx11-6 \              
    libxext6 \              
    libxi6 \
    libxcb-cursor0 \                
    libxcb1 \               
    libx11-xcb1 \           
    libxcb-icccm4 \         
    libxcb-image0 \
    libxkbcommon0 \         
    libxcb-keysyms1 \       
    libxcb-randr0 \         
    libxcb-render-util0 \   
    libxcb-shape0 \         
    libxcb-sync1 \          
    libxcb-xfixes0 \        
    libxcb-xinerama0 \      
    libxcb-xkb1 \           
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "__main__.py"]