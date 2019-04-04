use movies-api;

db.createCollection('movies');

db.movies.insert({
    title: "Fight Club",
    brazilian_title: "Clube da Luta",
    year_of_production: 1999,
    director: "David Fincher",
    genre: "Drama",
    cast: [
        {
            role: "Narrator",
            name: "Edward Norton"
        },
        {
            role: "Tyler Durden",
            name: "Brad Pitt"
        }
    ]
})

db.users.insert({
    name: "User 1",
    email: "user1@example.com",
    password: "$2b$10$Z/CTuXMo6/zKtkTcYI4lHe0p0aDnS6R/Pbi.ISH9NM7PbqjcWJXwC"
})