<?php
  echo "Hello!";
  $conn = mysqli_connect("localhost","root","","session.db");
  $sql = "Select * from sessions";
  $result = mysqli_query($conn, $sql);
?>

<!doctype html>
<html lang="en-US">
  <head>
    <meta charset="utf-8" />
    <title>Admin Dashboard</title>
  </head>
  <body>
    <h1>Admin Dashboard</h1>

    <table>
      <tr>
        <th>App Name</th>
        <th>ID</th>
        <th>State</th>
        <th>Create Time</th>
        <th>Update Time</th>
      </tr>

        <!-- <?php
        //while ($row = mysqli_fetch_assoc($result)) {
        ?>

        <tr>
          <td>
            <?php 
            // echo $row[''];
            ?>
          </td>
        </tr>

        <?php
        //}

      ?> -->

    </table>

    <!--
    <p>
        Placeholder
    </p>
    -->
  </body>
</html>