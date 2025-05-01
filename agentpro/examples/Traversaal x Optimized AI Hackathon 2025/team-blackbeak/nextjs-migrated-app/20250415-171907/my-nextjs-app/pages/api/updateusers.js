import db from '../../utils/db';

export default async (req, res) => {
  const { id, name, gender, username, password, address, email } = req.body;

  const query = 'UPDATE users SET name = ?, gender = ?, username = ?, password = ?, address = ?, email = ? WHERE id = ?';
  const values = [name, gender, username, password, address, email, id];

  try {
    await db.query(query, values);
    res.status(200).json({ message: 'User updated successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error updating user' });
  }
};