import db from '../../utils/db';

export default async (req, res) => {
  const { id } = req.query;

  const query = 'DELETE FROM users WHERE id = ?';
  const values = [id];

  try {
    await db.query(query, values);
    res.status(200).json({ message: 'User deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting user' });
  }
};