#!/bin/bash
cd ~/Desktop/AirVape_Shop
git init
git remote add origin https://github.com/dustymclean/airvape.git
touch CNAME
git add .
git commit -m "Initial commit: AirVape Storefront"
git branch -M main
git push -u origin main
