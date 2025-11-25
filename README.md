Imhotep: A Role-Based Medical Management System
Imhotep is a role-driven desktop application designed to modernize and centralize fundamental medical interactions within a healthcare environment. Built using Python (PyQt5) for the interface layer and MySQL/MariaDB for persistent storage, the system provides an integrated workflow linking doctors, patients, and pharmacists under a unified platform.
The primary objective of the application is to eliminate fragmented medical data handling by enabling seamless coordination between diagnosis, prescription generation, and medication dispensing. Through structured data models, secure user authentication, and compartmentalized interfaces, Imhotep delivers a consistent, reliable, and traceable medical information system.

Purpose and Scope
Imhotep addresses several critical needs within small-to-medium medical practices:
Centralized Record Management
Ensures that all medical history, prescriptions, and visit records are stored in an organized and query-friendly manner.
Role-Segregated Access
Doctors create and update prescriptions.
Patients view their medical records and suggestions.
Pharmacists access prescriptions and update dispensing status.
Secure User Authentication
All credentials are handled using industry-standard password hashing (bcrypt) to maintain confidentiality and prevent unauthorized access.
Streamlined Prescription Workflow
From the doctor’s creation to the pharmacist’s dispensing, each step is logged and managed through a consistent interface.
System Architecture
Imhotep is structured around a three-portal architecture, where each portal interacts with the same database but operates independently based on user role.

1. Doctor Portal
The Doctor Portal is designed for clinical data entry and case progression. Key functionalities include:
Patient search by unique identifier
Viewing previous case notes and prescription history
Generating new prescriptions
Updating existing medical records
Storing clinical suggestions, diagnoses, and prescribed medication
This portal ensures chronological case tracking and supports repeat follow-ups by maintaining structured patient histories.

2. Patient Portal
The Patient Portal provides a curated, read-only interface for patients to review:
Their personal information
Current prescriptions
Historical prescriptions
Doctor’s suggestions and notes
The portal emphasizes clarity and accessibility, enabling users to understand and follow their treatment plans without modification rights.

3. Pharmacist Portal
The Pharmacist Portal supports the medication dispensing workflow. Its primary responsibilities include:
Retrieving pending prescriptions
Reviewing the doctor’s notes and patient details
Updating dispensing status
Preventing duplication or unauthorized modification of medical entries
This structure ensures that the dispensing process remains controlled, auditable, and compliant with standard medical workflows.
