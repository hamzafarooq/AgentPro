import db from '../../utils/db';

export default async (req, res) => {
  const { id } = req.query;

  if (id) {
    const query = 'SELECT * FROM users WHERE id = ?';
    const values = [id];

    try {
      const [rows] = await db.query(query, values);
      res.status(200).json(rows[0]);
    } catch (error) {
      res.status(500).json({ error: 'Error fetching user' });
    }
  } else {
    const query = 'SELECT * FROM users ORDER BY username';

    try {
      const [rows] = await db.query(query);
      res.status(200).json(rows);
    } catch (error) {
      res.status(500).json({ error: 'Error fetching users' });
    }
  }
};