/**
 * Get all dealerships
 */

const Cloudant = require('@cloudant/cloudant');


function getDealershipCloudant(params) {
    const cloudant = Cloudant({
        url: params.COUCH_URL,
        plugins: { iamauth: { iamApiKey: params.IAM_API_KEY } }
    });
    return cloudant.db.use('dealerships');
}

async function main(params = {}) {
    if (params.state) {
        return await getDealerShipByState(params)
    }
    return await getAllDealerships(params)
}

async function getAllDealerships(params) {
    let dealershipsDB = getDealershipCloudant(params)

    try {
        let data = await dealershipsDB.list({ include_docs: true })
        return data['rows']
    } catch (err) {
        return { err: err.description }
    }
}

async function getDealerShipByState(params) {
    let dealershipsDB = getDealershipCloudant(params)
    try {
        return await dealershipsDB.find({ selector: { "st": params.state } })
    } catch (err) {
        return { err: err.description }
    }
}
