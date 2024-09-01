# Simple login
Just testing 2FA with emailing

To run, create a .env file with your email and "app password"

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
  session char(5) UNIQUE,
  otp_expiry timestamp NULL DEFAULT ((unix_timestamp() + (3 * 3600))
);
```
![image](https://github.com/user-attachments/assets/05f52f44-ba9d-4fff-817a-bca0fd3832cb)
![image](https://github.com/user-attachments/assets/ee986cc9-a1d9-4f38-b4be-4dea1b8b3236)

