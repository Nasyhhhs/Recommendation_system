# Personalized Post Recommendation System for Social Network

## Overview:
This project presents a personalized post recommendation system designed for a social network with the primary goal of enhancing user experience and increasing user satisfaction.

## Functionality:
The social network offers the following functionality:

Messaging feature to enable users to send messages to each other.
Creation of communities similar to groups in popular social networks.
Posting functionality to allow users to create and publish posts within communities.
During the registration process, students are required to fill out their profiles, which contain personal information. All profile data is stored in a postgres database.

## Project Objective:
The main objective of this project is to develop a sophisticated recommendation system that can provide personalized post recommendations for each user. The system achieves this by analyzing user profile characteristics, historical activity, and post content.

## Evaluation Metric:
The quality of the recommendation system will be evaluated using the hitrate@5 metric. This metric measures the effectiveness of recommendations based on a hidden set of users and timestamps.

## Project Plan:
The project consists of the following stages:

1. Data Exploration:
Data was loaded from the database into Jupyter Hub for a comprehensive data exploration.
2. Feature Engineering and Training Data Preparation:
Feature engineering will involve extracting relevant features from user profiles and post content.
The training data will be prepared using the extracted features and historical user interactions.
3. Model Training and Validation:
The recommendation model was trained on Jupyter Hub using the prepared training data.

4. Model Persistence:
The trained recommendation model is saved for future use.
5. Service Development:
A service was developed to load the saved model and provide personalized post recommendations based on user features.
6. Deployment and Testing:
The service and model could be deployed to the Cloud


Upon completion, the project will deliver a sophisticated recommendation system integrated into the social network, providing users with a personalized and enjoyable experience.
