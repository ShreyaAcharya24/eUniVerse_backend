# 🔐 GLS eUniverse – Backend

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-5.x-success)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue)
![Hosted on PythonAnywhere](https://img.shields.io/badge/Hosted%20on-PythonAnywhere-blue)

GLS eUniverse is a digital campus companion that enhances student experience, secures the campus environment, and promotes alumni engagement — all driven by a powerful Django backend

This repository powers the **core business logic and RESTful APIs** used by the mobile and admin panel of the eUniverse platform.

---

## 🚀 What It Does

- 🔑 Secure **role-based JWT authentication** for students, staff, guards, alumni, and admins.
- 📇 **Encrypted QR codes** (via Fernet) uniquely identify every university user — eliminating the need for physical ID cards.
- 🛡️ **Visitor entry logging system** for guards to register and monitor campus visits with photo, gate info, and timestamps.
- 🧾 Online **document request workflow** for to apply for important documents like transcripts, LORs, duplicate mark sheets etc. — with email notifications on status updates.
- 💬 **Alumni discussion portal** that enables alumni to share jobs, tips, and opportunities — moderated by admin approval.
- 🛠️ **Admin control panel logic** for managing programs, approving posts, and overseeing all users (manual + bulk upload).

---

## ⚙️ Tech Stack

| Component        | Tech Used              |
|------------------|------------------------|
| Backend          | Django                 |
| Auth             | JWT (JSON Web Token)   |
| QR-Encryption    | Fernet (cryptography)  |
| Database         | MySQL                  |
| Hosting          | PythonAnywhere         |

---

## 🔐 User Roles

- **Student**
- **Alumni**
- **Staff**
- **Guard**
- **Admin**

Each role has a tailored set of permissions and access to modules aligned with their real-world function.

## 👨‍💼 Project Leadership

This backend was architected and led by  [**Shreya Acharya**](https://github.com/ShreyaAcharya24) with direct responsibilities including:

- Developing mobile APIs
- Designing and handling QR encryption and profile logic
- Implementing post moderation and admin utilities
- Leading the team’s efforts to define and structure the full **Data Dictionary**
