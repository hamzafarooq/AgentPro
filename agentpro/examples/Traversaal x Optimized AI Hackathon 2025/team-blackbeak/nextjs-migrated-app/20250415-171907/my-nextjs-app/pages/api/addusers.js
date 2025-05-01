import db from '../../utils/db';

export default async (req, res) => {
  const { name, gender, username, password, address, email } = req.body;

  const query = 'INSERT INTO users (name, gender, username, password, address, email) VALUES (?, ?, ?, ?, ?, ?)';
  const values = [name, gender, username, password, address, email];

  try {
    await db.query(query, values);
    res.status(200).json({ message: 'User added successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error adding user' });
  }
};