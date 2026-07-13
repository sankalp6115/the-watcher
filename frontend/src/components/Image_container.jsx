import "./../styles/global.css"
import { useEffect, useState } from "react"
import { HOST, PORT } from "./BACKEND_URL"


const Image_container = ({ searchResults }) => {
    const [filenames, setFilenames] = useState([]);
    const BACKEND_URL = HOST + ":" + PORT;
    useEffect(() => {
        if (searchResults !== null) return;

        const fetchFilenames = async () => {
            const response = await fetch(BACKEND_URL + "/get-clusters");
            if (!response.ok) {
                throw new Error(response.status)
            }
            const result = await response.json();
            setFilenames(result);
        }
        fetchFilenames();
    }, [searchResults]);
    const imagesToDisplay = searchResults !== null ? searchResults : filenames;

    // Group images by cluster_id
    const groupedImages = imagesToDisplay.reduce((groups, imgObj) => {
        const cluster = imgObj.cluster_id;
        if (!groups[cluster]) {
            groups[cluster] = [];
        }
        groups[cluster].push(imgObj);
        return groups;
    }, {});

    return (
        <div className="gallery-wrapper" style={{ display: "flex", flexDirection: "column", gap: "30px", padding: "20px" }}>
            {Object.keys(groupedImages).length > 0 ? (
                Object.entries(groupedImages).map(([clusterId, images]) => (
                    <div key={clusterId} className="cluster-section">
                        <h2>{clusterId === "-1" ? "Noise / Unclustered" : `Cluster ${clusterId}`}</h2>
                        <div className="image_container" style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                            {images.map((imgObj) => (
                                <img src={`${HOST}:${PORT}/image/${imgObj.name}`} key={imgObj.id} alt={imgObj.name} style={{ width: "200px", height: "auto" }} />
                            ))}
                        </div>
                    </div>
                ))
            ) : (
                <p>{searchResults !== null ? "No results found" : "Loading images..."}</p>
            )}
        </div>
    )
}

export default Image_container