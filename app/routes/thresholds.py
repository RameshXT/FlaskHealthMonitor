from flask import Blueprint, request, jsonify
from services.threshold_service import update_thresholds, get_thresholds

thresholds_bp = Blueprint("thresholds", __name__)

@thresholds_bp.route("/thresholds", methods=["GET", "POST"])
def thresholds():
    if request.method == "POST":
        data = request.get_json()
        update_thresholds(data)
        return jsonify({"message": "Thresholds updated"}), 200
    else:
        return jsonify(get_thresholds()), 200
