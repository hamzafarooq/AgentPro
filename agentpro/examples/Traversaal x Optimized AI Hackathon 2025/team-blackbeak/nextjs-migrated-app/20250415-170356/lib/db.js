import mysql from 'mysql2/promise';

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'root',
  database: 'test',
});

export async function query(sql, params) {
  const [rows] = await pool.execute(sql, params);
  return rows;
}