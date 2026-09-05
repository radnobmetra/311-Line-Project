<?php
    // Start the session to manage user login state.
    session_start();

    // Checks if the form has been submitted by the user.
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Declares new variables to store the email and password from the POST request.
        $email = $_POST["emailLogin"];
        $password = $_POST["passLogin"];

        // CHANGE EMAIL AND PASSWORD HERE
        if ($email == "admin@cityofsacramento.org" && $password == "Sac@2026") {
            // Sets the user as logged in and saves their email.
            // $_SESSION stores data that persists across multiple pages.
            $_SESSION["user_logged_in"] = true;
            $_SESSION["user_email"] = $email;
            // Redirects the user to the dashboard page.
            header("Location: dashboard.php");
            exit;
        } else {
            // If either credential is incorrect, an error message will appear with this text.
            $_SESSION["login_error"] = "Invalid email or password.";

            // Stays on the login page and displays the error message.
            $_SESSION["user_logged_in"] = false;
            header("Location: login.php");
            exit;
        }
    }
?>

<!doctype html>
<html lang="en-US">
    <head>
        <meta charset="utf-8"/>
        <title>Login Page</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #121212; 
                color: #e0e0e0;
                margin: 20px;
            }
            
            h1 {
                color: #ffffff;
            }

            /* Styles for the email and password type input fields */
            input[type="email"], input[type="password"] {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 2px solid #333333; /* Width, style, color */
                border-radius: 5px; /* Rounded boarders */
                width: 100%;
                padding: 10px; /* All four sides */
                box-sizing: border-box;
            }

            label {
                display: block; /* Enables margins */
                margin-bottom: 5px;
            }

            /* Styles for the login button */
            button {
                background-color: #5ba755;
                color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                width: 100%;
                padding: 10px 20px; /* Top and bottom, left and right */
                margin: 5px 0;
                text-align: center;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover {
                opacity: 0.8;
            }

            /* Container holds all login elements */
            .container {
                background-color: #1e1e1e;
                border-radius: 5px;
                width: 50%;
                padding: 20px;
                /* Horizontally centers the container */
                margin-left: auto;
                margin-right: auto;
            }

            /* Each element is vertically separated */
            .element { 
                margin-bottom: 20px;
            }

            .error_message {
                color: #ff0000;
                width: 50%;
                padding-top: 5px;
            }
            
        </style>
    </head>
    <body>
        <h1>Login Page</h1>
        <div class="container">
            <!--
            name: The name or identifier for the login form.
            action: The endpoint where the form input data will be submitted for processing.
            method: "POST" hides the input data from the URL, but "GET" appends it.
            -->
            <form name="loginForm" action="" method="POST">
                <!--
                type: The type of input field (text is the default, but email and password can be used too).
                id: A unique identifier for the input field, used for labeling and scripting.
                required: Ensures that the user cannot submit the form without filling out this field.
                -->
                <!--Email input field-->
                <div class="element">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="emailLogin" placeholder="Your Email" required/>
                </div>
                <!--Password input field-->
                <div class="element">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="passLogin" placeholder="Your Password" required/>
                </div>

                <button type="submit">Login</button>

            </form>
            <!--If the form submission fails (the above PHP "else" statement), the hidden error message will be displayed.-->
            <?php if (isset($_SESSION["login_error"])): ?>
                <label class="error_message"><?php echo $_SESSION["login_error"]; ?></label>
                <!-- Clears the error message on page reload -->
                <?php unset($_SESSION["login_error"]); ?>
            <?php endif; ?>
            
        </div>
        
    </body>

</html>