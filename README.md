# Simple login
Just testing 2FA with emailing

To run, create a .env file with your email and "app password" (tested using a gmail account with app password)

```
email=""
app_password=""
```

Then start a mysql server, and create table `login` in database `testdb`:
```
CREATE TABLE login (
  username varchar(30) PRIMARY KEY,
  password varchar(30) NOT NULL,
  otp INT,
  email varchar(50),
  verified BOOL,
  session char(5),
  otp_expiry timestamp NULL DEFAULT ((unix_timestamp() + (3 * 3600))
);
```
![image](https://github.com/user-attachments/assets/17a0694d-20ec-4243-943a-5a5f6ebc8601)


improvements that could be done:
hashing passwords using bcrypt and unique constraint on sessions 
