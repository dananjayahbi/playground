const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

require("dotenv").config();

const app = express();
const PORT = 5000;
const JWT_SECRET = process.env.JWT_SECRET;

app.use(express.json());

// Middleware to protect routes
const authenticateToken = (req, res, next) => {
  const token = req.headers["authorization"]?.split(" ")[1];
  if (!token) return res.sendStatus(401);

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

// User registration route
app.post("/register", async (req, res) => {
  const { name, email, password } = req.body;

  // Hash the password
  const hashedPassword = await bcrypt.hash(password, 10);

  try {
    const user = await prisma.user.create({
      data: {
        name,
        email,
        password: hashedPassword,
      },
    });
    res.json(user);
  } catch (error) {
    res.status(400).json({ error: "User with this email already exists" });
  }
});

// User login route
app.post("/login", async (req, res) => {
  const { email, password } = req.body;

  const user = await prisma.user.findUnique({
    where: { email },
  });

  if (!user)
    return res.status(400).json({ error: "Invalid email or password" });

  const isValidPassword = await bcrypt.compare(password, user.password);
  if (!isValidPassword)
    return res.status(400).json({ error: "Invalid email or password" });

  // Generate JWT
  const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, {
    expiresIn: "1h",
  });
  res.json({ token });
});

// Get all users (protected route)
app.get("/users", authenticateToken, async (req, res) => {
  const users = await prisma.user.findMany();
  res.json(users);
});

// Update user (protected route)
app.put("/users/:id", authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { name, email } = req.body;

  try {
    const updatedUser = await prisma.user.update({
      where: { id },
      data: { name, email },
    });
    res.json(updatedUser);
  } catch (error) {
    res.status(404).json({ error: "User not found" });
  }
});

// Delete user (protected route)
app.delete("/users/:id", authenticateToken, async (req, res) => {
  const { id } = req.params;

  try {
    await prisma.user.delete({
      where: { id },
    });
    res.json({ message: "User deleted" });
  } catch (error) {
    res.status(404).json({ error: "User not found" });
  }
});

// Create a new post
app.post("/posts", authenticateToken, async (req, res) => {
  const { description } = req.body;
  const userId = req.user.userId;

  try {
    // Find the user to get their name
    const user = await prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user) return res.status(404).json({ error: "User not found" });

    const post = await prisma.post.create({
      data: {
        description,
        userId: user.id,
        userName: user.name,
      },
    });
    res.json(post);
  } catch (error) {
    res.status(400).json({ error: "Error creating post" });
  }
});

// Get all posts (public)
app.get("/posts", async (req, res) => {
  const posts = await prisma.post.findMany();
  res.json(posts);
});

// Get posts by a specific user (protected)
app.get("/posts/user/:userId", authenticateToken, async (req, res) => {
  const { userId } = req.params;

  const posts = await prisma.post.findMany({
    where: { userId },
  });

  res.json(posts);
});

// Update a post (protected)
app.put("/posts/:id", authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { description } = req.body;
  const userId = req.user.userId;

  try {
    // Check if the post belongs to the user
    const post = await prisma.post.findUnique({
      where: { id },
    });

    if (!post) return res.status(404).json({ error: "Post not found" });
    if (post.userId !== userId)
      return res.status(403).json({ error: "Unauthorized" });

    const updatedPost = await prisma.post.update({
      where: { id },
      data: { description },
    });

    res.json(updatedPost);
  } catch (error) {
    res.status(400).json({ error: "Error updating post" });
  }
});

// Delete a post (protected)
app.delete("/posts/:id", authenticateToken, async (req, res) => {
  const { id } = req.params;
  const userId = req.user.userId;

  try {
    // Check if the post belongs to the user
    const post = await prisma.post.findUnique({
      where: { id },
    });

    if (!post) return res.status(404).json({ error: "Post not found" });
    if (post.userId !== userId)
      return res.status(403).json({ error: "Unauthorized" });

    await prisma.post.delete({
      where: { id },
    });

    res.json({ message: "Post deleted" });
  } catch (error) {
    res.status(400).json({ error: "Error deleting post" });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
