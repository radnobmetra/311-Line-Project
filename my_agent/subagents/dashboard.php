<?php
  $conn = new SQLite3('../.adk/session.db');
  $sql = "Select * from sessions";
  $result = $conn->query($sql);
?>

<!doctype html>
<html lang="en-US">
  <head>
    <meta charset="utf-8" />
    <title>Admin Dashboard</title>

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

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background-color: #1e1e1e;
  }

  th, td {
    border: 1px solid #333;
    padding: 12px 15px;
    text-align: left;
  }

  td:nth-child(2) {
    word-break: break-all;
  }
  
  th:nth-child(3), td:nth-child(3) {
    width: 35%;
    word-break: break-word;
  }

  th {
    background-color: #2c2c2c;
    color: #4da6ff;
    font-weight: bold;
    font-size: 1.25em;
  }

  tr:nth-child(even) {
    background-color: #252525;
  }
</style>

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

      <?php
      while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
      ?>
        <tr>
          <td><?php echo $row['app_name']; ?></td>
          <td><?php echo $row['id']; ?></td>
          <td><?php echo $row['state']; ?></td>
          <td><?php echo $row['create_time']; ?></td>
          <td><?php echo $row['update_time']; ?></td>
        </tr>

      <?php
      }
      ?> 

    </table>

    <!--
    <p>
        Placeholder
    </p>
    -->
  </body>
</html>