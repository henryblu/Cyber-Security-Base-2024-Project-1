# Cyber-Security-Base-2024-Project-1

This repository contains my Cyber Security Base Course Project, which demonstrates five different security flaws from the [OWASP 2021 list](https://owasp.org/www-project-top-ten/) plus an additional CSRF flaw.

Link to repository: [https://github.com/henryblu/Cyber-Security-Base-2024-Project-1](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1)

## Installation Instructions

To use the demo project, download and extract the project files and run the following command:
```bash
python manage.py runserver
```

If the database isn't working correctly, run the following commands as well:
```bash
python manage.py makemigrations
python manage.py migrate
```

Once set up, you can access the login page from: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Existing Users

- **Player 1**:
  - Username: admin
  - Email: admin@admin.com
  - Password: admin

- **Player 2**:
  - Username: test
  - Email: test@test.com
  - Password: test

- **Player X**:
  - Feel free to create your own account :)

## Flaws in the Project

### FLAW 1: Broken Access Control
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L70)
[Link to Template Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/templates/blackjack_app/base.html#L31)
[Link to Template Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/templates/blackjack_app/home.html#L19)

**Description**: The vulnerability involves using user input to fetch a user profile directly by retrieving the profile ID from a GET parameter. This approach does not verify the ownership of the profile, thereby allowing an attacker to manipulate the `profile_id` parameter to access other users' profiles and sensitive information. Foe example, a logged in user with profile_id=1 can access another user's profile by modifying the URL to include a different `profile_id` parameter, e.g.:
http://127.0.0.1:8000/profile/?profile_id=2
Such broken access control flaws are critical as they can lead to unauthorized data exposure such as the users playing the game, their email, and other personal information.


**Fix**: The fix involves modifying the code to ensure that the profile fetched belongs to the currently authenticated user rather than relying on the `profile_id` from the GET parameter. This can be done by using the authenticated user's information, ensuring that users can only access their own profiles.

### FLAW 2: Injection
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L188)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L210)

**Description**:  The code is vulnerable to SQL injection attacks, a type of security flaw where an attacker can manipulate an SQL query by injecting arbitrary code into it. In the place_bet view, the cursor.execute method constructs an SQL query directly. Although it uses parameterized queries, which is generally a good practice, the vulnerability arises from not fully leveraging Django's ORM capabilities. If an attacker gains control over the new_money parameter, they could potentially manipulate the query to execute malicious SQL commands, such as modifying data or retrieving sensitive information.

**Fix**: The fix involves using Django’s ORM to update the user’s money instead of directly constructing an SQL query. This change ensures that the user input is sanitized and prevents SQL injection attacks.
### FLAW 3: Insecure Design (No Validation for Game State)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L94)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L109)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L150)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L191)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L235)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L247)

**Description**: The code does not validate the game state before allowing the user to perform certain actions. Although the web UI only allows navigation in a way that should not cause any errors, the lack of checks enables users to manipulate the URL to trigger actions such as determining the winner, resetting the game, or ending the game when these actions are not meant to occur. This can lead to unexpected behavior, such as backing out of a bet after seeing the cards, gaining infinite money after winning one game by refreshing the page, or accidentally deleting an account by triggering the end game before the game is meant to be over.

**Fix**: Implement proper validation checks to ensure that users can only perform actions based on the current game state. For example, before allowing a user to place a bet, check that the game is not already in progress. This will prevent users from performing actions that are not allowed at that point in the game.

### FLAW 4: Identification and Authentication Failures (Weak Password Policy)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/forms.py#L7)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L31)

**Description**: The custom registration form in the project allows users to create accounts with weak passwords. The form does not enforce strong password policies, making users susceptible to brute force attacks and credential stuffing. Attackers can exploit this vulnerability by using automated tools to try common passwords or leaked password databases to gain unauthorized access to user accounts. This is a significant security risk as it can lead to compromising user data and can lead to further attacks on the system using the compromised accounts.

**Fix**: The fix involves replacing the custom registration form with Django's `UserCreationForm`, which includes built-in password validation to enforce strong password policies. This ensures that users create passwords that are complex and harder to guess, enhancing the overall security of the application.

### FLAW 5: Cross-Site Request Forgery (CSRF)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/templates/blackjack_app/game.html#L5)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/templates/blackjack_app/login.html#L7)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/templates/blackjack_app/place_bet.html#L7)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/templates/blackjack_app/register.html#L6)

**Description**: Cross-Site Request Forgery (CSRF) is a security flaw that occurs when a malicious website tricks a user’s browser into performing unwanted actions on a different site where the user is authenticated. In this project, the forms do not include CSRF tokens, making them vulnerable to such attacks. For example, an attacker can craft a malicious form on their website that submits a request to the game’s `place_bet` endpoint. If the user is logged into the game site, the browser will submit this request with the user’s credentials, allowing the attacker to place bets without the user's consent.

**Fix**: The solution involves adding CSRF tokens to all forms. Django provides built-in CSRF protection, which generates unique tokens for each form submission. Including these tokens ensures that the forms can only be submitted from the same site, preventing malicious requests from being executed. 


### FLAW 6: Security Logging and Monitoring Failures
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/blackjack_app/views.py#L55)
[Link to Source](https://github.com/henryblu/Cyber-Security-Base-2024-Project-1/blob/main/config/settings.py#L127)

**Description**: The code does not include security logging and monitoring to track and detect security incidents such as failed login attempts. Without logging, failed login attempts go unnoticed, making it difficult to detect potential brute force attacks or credential stuffing attacks where attackers systematically test multiple passwords. This flaw could be exploited by an attacker who uses automated tools to try a large number of username and password combinations without detection. Such attacks could eventually lead to unauthorized access if a weak or commonly used password is guessed. Regular monitoring of logs can alert administrators to unusual activities, such as a high number of failed login attempts, allowing for timely intervention to block or mitigate the attack.

**Fix**: Add security logging to track and monitor security incidents. Django provides built-in logging that allows developers to log security events such as failed login attempts. This can be done by configuring a logger in the settings and using it in views to log failed attempts.