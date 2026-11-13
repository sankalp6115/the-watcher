import { useEffect, useState } from "react"
import { HOST, PORT } from "./BACKEND_URL"

const Searchbar = ({ onSearchResults }) => {
    const [search, setSearch] = useState("");
    const BACKEND_URL = HOST + ":" + PORT;

    useEffect(() => {
        if (!search.trim()) {
            onSearchResults(null);
            return;
        }
        const searchResult = async (query) => {
            try {
                const response = await fetch(BACKEND_URL + `/image/search/${query}`);
                if (!response.ok) {
                    throw new Error(response.status)
                }
                const result = await response.json();
                console.log(result)
                onSearchResults(result);
            } catch (err) {
                console.error("Search failed", err);
            }
        }

        const timerId = setTimeout(() => {
            searchResult(search);
        }, 1000);

        return () => clearTimeout(timerId);
    }, [search]);

    return (
        <div>
            <input type="search" name="search" id="search" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
    )
}

export default Searchbar