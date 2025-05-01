import React from 'react';
import { useRouter } from 'next/router';

const FrontendNavigation = ({ posts }) => {
  const router = useRouter();

  const handleSearch = (e) => {
    e.preventDefault();
    const searchTerm = e.target.search.value;
    router.push(`/search?search=${searchTerm}`);
  };

  return (
    <div className="navigation">
      <div className="search">
        <form onSubmit={handleSearch}>
          <input type="text" name="search" placeholder="search" style={{ borderRadius: '5px', height: '30px', width: '200px' }} />
          <input type="submit" value="OK" style={{ borderRadius: '5px', height: '35px' }} />
        </form>
      </div>
      {posts.map((post) => (
        <ul key={post.id} style={{ listStyle: 'none', fontFamily: "'Courier New', Courier, monospace", color: '#999999', border: 'solid 5px #000033' }}>
          <li>{post.date}</li>
          <li>{post.title}</li>
          <li>{post.author}</li>
          <li><img src={`/image/${post.image}`} height="100px" width="150px" alt={post.title} /></li>
          <li>{post.content}</li>
        </ul>
      ))}
    </div>
  );
};

export default FrontendNavigation;