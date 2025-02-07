# **Jade Circuit Simulator - Extended Version**

## **Project Overview**
This project is an extension of [Jade](https://github.com/6004x/jade), a circuit simulation tool. As part of our **Digital System Design** course, we cloned the original repository and enhanced it with new features to improve usability and functionality.

Jade allows users to configure simulation tools and part libraries for different assignments. The default configuration (`jade_standalone.html`) displays all available tools and libraries. Users can also load specific libraries with schematics, icons, and (read-only) tests that serve as templates and test jigs for design problems.

## **New Features Added**
We have extended the functionality of Jade by adding the following features:

- **Database Enhancements:**  
  - Implemented **One-to-One** and **One-to-Many** database relationships.  
- **OTP (One-Time Password):**  
  - Added email-based OTP functionality for authentication.  
- **Authentication & Authorization:**  
  - Secure user authentication and role-based authorization.  
- **Simulation Sharing:**  
  - Users can share their circuit simulations with other users.  
- **Saving Simulations:**  
  - Each user can save their simulations in the database for future access.  
- **User Profiles:**  
  - Created personal profile pages for users, which include:  
    - **Followers** (user connections).  
    - **Personal simulations** (saved and shared circuits).  

## **File Guide**
The four main files (`main`, `otp`, `model`, `cntl`) are located in the `dev` folder.

- **Model**: Contains code related to the database.  
- **Otp**: Used for sending authentication via email.  
- **Cntl**: The main location for Flask code and URLs.  

The HTML code is divided into sections and placed in the main folder.

### **Important Note**
If you need to create the database file, follow these steps:  

1. Delete the existing **migration** folder in `dev`.  
2. Open **CMD** in the `dev` folder and run the following commands:  

```sh
python -m flask --app model db init
python -m flask --app model db merge
python -m flask --app model db upgrade
python -m flask --app model db migrate
python -m flask --app model db upgrade
```

(These commands may vary depending on the version, so adjustments may be required. The file is **portable**, meaning you do not need to enter these commands again.)

### **Project Portability**
Files such as `pdm-build` or `venv` are included to ensure the project remains portable.
