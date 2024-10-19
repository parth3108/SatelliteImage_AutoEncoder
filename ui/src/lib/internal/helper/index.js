import { HardDrive } from "lucide-svelte"
import { Workflow } from "lucide-svelte"
import { ChartScatter } from "lucide-svelte"
import { Upload } from "lucide-svelte"
import { FolderKanban } from "lucide-svelte"
import { GitPullRequestCreateArrow } from "lucide-svelte"
import { GitBranch } from "lucide-svelte"

const SideBarMenu = [
    {
        "name": "Datasets",
        "icon": HardDrive,
        "subMenu": [
            {
                "name": "View Dataset",
                "icon": FolderKanban,
                "path": "/datasets/view"
            }
        ]
    },
    {
        "name": "Pipeline",
        "icon": Workflow,
        "subMenu": [
            {
                "name": "Edit Pipeline",
                "icon": GitPullRequestCreateArrow,
                "path": "/pipeline/edit"
            },
            {
                "name": "View Pipeline",
                "icon": GitBranch,
                "path": "/pipeline/view"
            }
        ]
    },
    {
        "name": "Evaluation",
        "icon": ChartScatter,
        "path": "/evaluation"
    },
]


const createPipe = (pipe) => {
    let parsedPipe = {};
    parsedPipe["execution_path"] = `${pipe["module"]}:${pipe["method"]}`;
    parsedPipe["params"] = {};

    pipe["parameters"].forEach(element => {

        if (element["value"] === undefined || element["value"] === null || element["value"] === "") {
            // ignore
        } else {
            if (element["type"] == 'str') {
                parsedPipe["params"][element["field"]] = element["value"]
            } else if (element["type"] == 'int') {
                parsedPipe["params"][element["field"]] = Number(element["value"])
            } else if (element["type"] == 'list') {
                parsedPipe["params"][element["field"]] = element["value"].split(",").map(vl => {
                    return Number(vl)
                });
            } else if (element["type"] == 'bool') {
                parsedPipe["params"][element["field"]] = element["value"] === "true" ? true : false;
            } else if (element["type"] == 'float') {
                try {
                    parsedPipe["params"][element["field"]] = parseFloat(element["value"]);
                } catch (error) {
                    alert("Invalid Value for " + element["field"]);
                    return;
                }
            } else {
                parsedPipe["params"][element["field"]] = element["value"];
            }
        }

    });

    return parsedPipe;
}

const createPipeline = (pipeline) => {
    let parsedPipeline = [];
    if (!pipeline) {
        throw new Error("Invalid Pipeline");
    } else if (pipeline.length == 0) {
        throw new Error("No Pipes in Pipeline");
    } else {
        for (let index = 0; index < pipeline.length; index++) {
            parsedPipeline.push(createPipe(pipeline[index]));
        }
    }

    return parsedPipeline;
}

export {
    SideBarMenu,
    createPipe,
    createPipeline
}