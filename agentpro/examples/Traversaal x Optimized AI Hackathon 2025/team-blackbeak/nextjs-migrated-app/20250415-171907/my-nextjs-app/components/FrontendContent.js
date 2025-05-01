import React from 'react';
import Link from 'next/link';

const FrontendContent = ({ posts, pageNo, totalPages }) => (
  <div className="content">
    {posts.map((post) => (
      <ul key={post.id} style={{ listStyle: 'none', fontFamily: "'Courier New', Courier, monospace", color: '#999999', border: 'solid 5px #000033' }}>
        <li>{post.date}</li>
        <li>{post.title}</li>
        <li>{post.author}</li>
        <li>{post.keyword}</li>
        <li><img src={`/image/${post.image}`} height="100px" width="150px" alt={post.title} /></li>
        <li>{post.content.substring(0, 20)}<Link href={`/readmoreall?id=${post.id}`}>Read More...</Link></li>
      </ul>
    ))}
    <div className="pagination">
      {pageNo > 1 && <Link href={`/blogs?page_no=${pageNo - 1}`}>Previous</Link>}
      {Array.from({ length: totalPages }, (_, i) => (
        <Link key={i} href={`/blogs?page_no=${i + 1}`}>{i + 1}</Link>
      ))}
      {pageNo < totalPages && <Link href={`/blogs?page_no=${pageNo + 1}`}>Next</Link>}
    </div>
  </div>
);

export default FrontendContent;