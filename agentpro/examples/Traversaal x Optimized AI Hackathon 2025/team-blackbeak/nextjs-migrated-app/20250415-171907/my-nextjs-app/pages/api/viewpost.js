import db from '../../utils/db';

export default async (req, res) => {
  const { id, page_no, limit } = req.query;

  if (id) {
    const query = 'SELECT * FROM posts WHERE id = ?';
    const values = [id];

    try {
      const [rows] = await db.query(query, values);
      res.status(200).json(rows[0]);
    } catch (error) {
      res.status(500).json({ error: 'Error fetching post' });
    }
  } else if (page_no) {
    const noOfRowsPerPage = 2;
    const offset = (page_no - 1) * noOfRowsPerPage;

    const query = 'SELECT * FROM posts ORDER BY author ASC LIMIT ? OFFSET ?';
    const values = [noOfRowsPerPage, offset];

    try {
      const [rows] = await db.query(query, values);
      res.status(200).json(rows);
    } catch (error) {
      res.status(500).json({ error: 'Error fetching posts' });
    }
  } else if (limit) {
    const query = 'SELECT * FROM posts ORDER BY id DESC LIMIT ?';
    const values = [limit];

    try {
      const [rows] = await db.query(query, values);
      res.status(200).json(rows);
    } catch (error) {
      res.status(500).json({ error: 'Error fetching recent posts' });
    }
  } else {
    const query = 'SELECT * FROM posts ORDER BY author';

    try {
      const [rows] = await db.query(query);
      res.status(200).json(rows);
    } catch (error) {
      res.status(500).json({ error: 'Error fetching posts' });
    }
  }
};