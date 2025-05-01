import db from '../../utils/db';

export default async (req, res) => {
  const { username, password } = req.body;

  const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
  const values = [username, password];

  try {
    const [rows] = await db.query(query, values);
    if (rows.length === 0) {
      res.status(401).json({ error: 'Invalid username or password' });
    } else {
      req.session.username = username;
      res.status(200).json({ message: 'Login successful' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Error logging in' });
  }
};