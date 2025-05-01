import { IncomingForm } from 'formidable';
import fs from 'fs';
import path from 'path';
import db from '../../utils/db';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async (req, res) => {
  const form = new IncomingForm();
  form.parse(req, async (err, fields, files) => {
    if (err) {
      return res.status(500).json({ error: 'Error parsing form data' });
    }

    const { title, author, keyword, content, date } = fields;
    const image = files.image;

    const validExtensions = ['jpeg', 'jpg', 'bmp', 'png', 'gif'];
    const ext = path.extname(image.name).toLowerCase().replace('.', '');
    const userpic = `img_${Math.floor(Math.random() * 1000000)}.${ext}`;

    if (validExtensions.includes(ext)) {
      const oldPath = image.path;
      const newPath = path.join(process.cwd(), 'public', 'image', userpic);

      fs.rename(oldPath, newPath, async (err) => {
        if (err) {
          return res.status(500).json({ error: 'Error saving image' });
        }

        const query = 'INSERT INTO posts (title, author, keyword, image, content, date) VALUES (?, ?, ?, ?, ?, ?)';
        const values = [title, author, keyword, userpic, content, date];

        try {
          await db.query(query, values);
          res.status(200).json({ message: 'Post added successfully' });
        } catch (error) {
          res.status(500).json({ error: 'Error adding post' });
        }
      });
    } else {
      res.status(400).json({ error: 'Invalid image extension' });
    }
  });
};