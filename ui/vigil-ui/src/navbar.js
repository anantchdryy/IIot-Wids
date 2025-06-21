import React from 'react';
import { NavLink } from 'react-router-dom';
import logo from './logo.svg';      
import './navbar.css';

export default function Navbar() {
  return (
    <nav>
      <NavLink to="/home" className="logo-link">
        <img src={logo} alt="VĪGĪL logo" className="nav-logo" />
      </NavLink>

      <ul>
        <li>
          <NavLink
            to="/analytics"
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            Analytics
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/about"
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            About
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
