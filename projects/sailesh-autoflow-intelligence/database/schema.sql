CREATE DATABASE IF NOT EXISTS autoflow_intelligence;
USE autoflow_intelligence;

CREATE TABLE vehicles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  vin VARCHAR(32) UNIQUE NOT NULL,
  brand VARCHAR(80) NOT NULL,
  model VARCHAR(100) NOT NULL,
  year INT NOT NULL,
  category VARCHAR(60) NOT NULL,
  fuel_type VARCHAR(60) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  mileage INT NOT NULL,
  status VARCHAR(40) NOT NULL,
  margin DECIMAL(10,2) NOT NULL,
  days_in_stock INT NOT NULL,
  image_url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leads (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_name VARCHAR(120) NOT NULL,
  preferred_vehicle VARCHAR(160) NOT NULL,
  source VARCHAR(80) NOT NULL,
  temperature VARCHAR(30) NOT NULL,
  budget DECIMAL(10,2) NOT NULL,
  status VARCHAR(60) NOT NULL,
  next_action VARCHAR(160) NOT NULL,
  assigned_to VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE activities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lead_id INT,
  activity_type VARCHAR(80) NOT NULL,
  notes TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE TABLE monthly_targets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  month_name VARCHAR(20) NOT NULL,
  revenue_target DECIMAL(12,2) NOT NULL,
  actual_revenue DECIMAL(12,2) NOT NULL,
  leads_target INT NOT NULL,
  actual_leads INT NOT NULL
);

