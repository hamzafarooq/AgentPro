import React, { useState } from 'react';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

const AddPost = ({ username }) => {
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    keyword: '',
    content: '',
    date: '',
    image: null,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, image: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    Object.keys(formData).forEach((key) => {
      data.append(key, formData[key]);
    });

    const res = await fetch('/api/addpost', {
      method: 'POST',
      body: data,
    });

    if (res.ok) {
      window.location.href = '/viewpost';
    }
  };

  return (
    <>
      <Header />
      <Navigation username={username} />
      <div className="content">
        <form onSubmit={handleSubmit} encType="multipart/form-data">
          <label>
            Title:
            <input type="text" name="title" value={formData.title} onChange={handleChange} />
          </label>
          <br />
          <label>
            Author:
            <input type="text" name="author" value={formData.author} onChange={handleChange} />
          </label>
          <br />
          <label>
            Keyword:
            <input type="text" name="keyword" value={formData.keyword} onChange={handleChange} />
          </label>
          <br />
          <label>
            Image:
            <input type="file" name="image" onChange={handleFileChange} />
          </label>
          <br />
          <label>
            Content:
            <textarea name="content" value={formData.content} onChange={handleChange}></textarea>
          </label>
          <br />
          <label>
            Date:
            <input type="date" name="date" value={formData.date} onChange={handleChange} />
          </label>
          <br />
          <input type="submit" value="Submit" />
        </form>
      </div>
      <Footer />
    </>
  );
};

export async function getServerSideProps({ req }) {
  const { username } = req.session;

  if (!username) {
    return {
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }

  return { props: { username } };
}

export default AddPost;